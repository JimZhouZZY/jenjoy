import argparse
import os
import shutil
import subprocess
import sys

def check_vim_available():
    if shutil.which("vim") is None:
        print("❌ vim is not available in PATH. Please install vim for auto-formatting.")
        sys.exit(1)

def format_with_vim(filepath):
    if not os.path.isfile(filepath):
        print(f"❌ {filepath} is not a file.")
        sys.exit(1)
    try:
        subprocess.run([
            "vim", "--clean",
            "-c", "set tabstop=4",
            "-c", "set shiftwidth=4",
            "-c", "set expandtab",
            "-c", "gg=G",
            "-c", "wq",
            filepath
        ], check=True)
        print(f"✅ File formatted with vim: {filepath}")
    except Exception as e:
        print(f"⚠️  Failed to format file with vim: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Format a file using vim auto-indent (gg=G) and 4-space tabs.")
    parser.add_argument("file", help="File to format")
    args = parser.parse_args()

    check_vim_available()
    format_with_vim(args.file)

if __name__ == "__main__":
    main()