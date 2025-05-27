# TODO: methods that already have doc comments should be skipped

import argparse
import os
import re
import sys
import requests
import shutil
import subprocess
import threading

from tree_sitter import Language, Parser

DEEPSEEK_API_URL = "http://172.18.36.55:5001/api/v1/chat/completions"

# Build the language library if not already built
LIB_PATH = os.path.join(os.path.dirname(__file__), "build", "my-languages.so")
JAVA_LANGUAGE_REPO = os.path.join(os.path.dirname(__file__), "tree-sitter-java")
if not os.path.exists(LIB_PATH):
    Language.build_library(
        # Store the library in the `build` directory
        LIB_PATH,
        [
            JAVA_LANGUAGE_REPO,
        ]
    )
JAVA_LANGUAGE = Language(LIB_PATH, "java")

def extract_doc_comment(text):
    """Extract the last /** ... */ doc comment block from text."""
    start = text.rfind("/**")
    if start != -1:
        # Search forward for the first non-whitespace character before /** to preserve indentation
        prefix = re.search(r"[ \t]*$", text[:start])
        if prefix:
            start = prefix.start()
    end = text.find("*/", start)
    if start != -1 and end != -1:
        return text[start:end+2]
    return text

def insert_doc_comment(java_code, doc_comment):
    """Insert doc_comment before the first non-empty line of java_code, preserving indentation."""
    lines = java_code.splitlines()
    for idx, line in enumerate(lines):
        if line.strip():
            indent = re.match(r"\s*", line).group(0)
            break
    else:
        indent = ""
        idx = 0
    doc_comment_indented = "\n".join(
        indent + l if l.strip() else l for l in doc_comment.splitlines()
    )
    return "\n".join(lines[:idx]) + ("\n" if idx > 0 else "") + doc_comment_indented + "\n" + "\n".join(lines[idx:])

def call_deepseek(api_key, java_code):
    prompt = (
        "Add a detailed doc comment to the following java method or class:\n"
        f"{java_code}\n"
        "The doc comment should describe what the method or class does. "
        "Only output the doc comment for the following java code, wrapped with /** ... */. "
        "Do not output the method code or any explanation.\n"
        "Don't include any explanations in your response."
    )
    payload = {
        "model": "deepseek-r1-standard",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        print(f"DeepSeek request failed: {e}")
        sys.exit(1)
    return resp.text

def count_tokens(text):
    # Simple token count: split by whitespace and punctuation
    return len(re.findall(r"\w+|[^\w\s]", text, re.UNICODE))

def get_method_nodes(source_code):
    """
    Parse Java source code and yield (start_byte, end_byte, method_source, has_doc_comment) for each method/class.
    """
    parser = Parser()
    parser.set_language(JAVA_LANGUAGE)
    tree = parser.parse(bytes(source_code, "utf8"))
    root = tree.root_node

    def get_node_text(node):
        return source_code[node.start_byte:node.end_byte]

    # Find all method_declaration and class_declaration nodes
    result = []
    def visit(node):
        if node.type in ("method_declaration", "class_declaration", "constructor_declaration"):
            # Check for doc comment immediately above
            start_line = node.start_point[0]
            lines = source_code.splitlines()
            has_doc = False
            method_start = node.start_byte
            # Look for /** ... */ in the lines above
            for i in range(start_line-1, max(-1, start_line-6), -1):
                if i < 0: break
                if re.search(r"/\*\*.*\*/", lines[i]):
                    has_doc = True
                    break
                if lines[i].strip() == "":
                    continue
                if not lines[i].strip().startswith("*") and not lines[i].strip().startswith("//"):
                    break
            result.append((node.start_byte, node.end_byte, get_node_text(node), has_doc))
        for child in node.children:
            visit(child)
    visit(root)
    return result

def write_code_snippet_to_file(file_path, original_code, modified_code):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
        start_pos = file_content.find(original_code)
        if start_pos != -1:
            end_pos = start_pos + len(original_code)
            modified_content = (
                file_content[:start_pos]
                + modified_code
                + file_content[end_pos:]
            )
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(modified_content)

def check_vim_available():
    if shutil.which("vim") is None:
        print("❌ vim is not available in PATH. Please install vim for auto-formatting.")
        sys.exit(1)

def format_with_vim(filepath):
    try:
        subprocess.run([
            "vim", "--clean",
            "-c", "set tabstop=4",
            "-c", "set shiftwidth=4",
            "-c", "set expandtab",
            "-c", "normal gg=G",
            "-c", "wq",
            filepath
        ], check=True)
        print(f"✅ File formatted with vim: {filepath}")
    except Exception as e:
        print(f"⚠️  Failed to format file with vim: {e}")

def send_stop_request(api_key):
    url = "http://172.18.36.55:5001/api/v1/stop"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        if resp.ok:
            print("✅ Stop request sent successfully")
        else:
            print(f"⚠️  Stop request failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"⚠️  Failed to send stop request: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate Java doc comments for each method/class using DeepSeek LLM.")
    parser.add_argument("file", help="Java file to process")
    parser.add_argument("-o", "--output", help="Output file name (default: overwrite input file)")
    parser.add_argument("--api-key", required=True, help="DeepSeek API key")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        sys.exit(f"File {args.file} does not exist.")

    with open(args.file, "r", encoding="utf-8") as f:
        java_code = f.read()

    method_nodes = get_method_nodes(java_code)
    generated_doc_comments = {}

    try:
        for start, end, method_source, has_doc in method_nodes:
            if has_doc:
                print("⚠️  Method/class already has a doc comment. Skipping...")
                continue
            tokens = count_tokens(method_source)
            if tokens > 2048:
                print("⚠️  Method/class too long, skipping...")
                continue
            print(f"🔧 Generating doc comment for method/class at bytes {start}-{end} ...")
            print("==== Raw Input ====")
            print(method_source)
            llm_output = call_deepseek(args.api_key, method_source)
            lines = llm_output.splitlines()
            comment_parts = []
            for line in lines:
                content = line.replace("data: ", "", 1)
                # Replace all occurrences of [h_newline] with a newline in the content
                content = re.sub(r"\[h_newline\]", "\n", content)
                comment_parts.append(content)
                
            code = "".join(comment_parts)
            doc_comment = extract_doc_comment(code)
            merged_code = insert_doc_comment(method_source, doc_comment)
            generated_doc_comments[method_source] = merged_code
            print("==== Doc Output ====")
            print(doc_comment)
            print(f"✅ Doc comment generated.")
    except KeyboardInterrupt:
        print("⏹️  Generation interrupted by user, sending stop request...")
        send_stop_request(args.api_key)
        sys.exit(1)

    # Write back all changes
    output_file = args.output if args.output else args.file
    file_content = java_code
    for original_code, merged_code in generated_doc_comments.items():
        file_content = file_content.replace(original_code, merged_code)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"✅ All doc comments generated and written to {output_file}")
    format_with_vim(output_file)

if __name__ == "__main__":
    main()