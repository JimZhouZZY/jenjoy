# Jenjoy

Jenjoy helps you write Java doc comments automatically using LLMs and formats your code with Vim.

## Features

- Automatically generates Javadoc comments for Java methods and classes.
- Skips methods/classes that already have doc comments.
- Uses [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for Java code parsing.
- Optionally formats Java files using Vim (if available).

## Requirements

- Python 3
- [tree-sitter](https://github.com/tree-sitter/py-tree-sitter) Python bindings
- Vim (for code formatting, optional but recommended)
- Python packages in requirements.txt

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
python jenjoy.py <yourfile.java> --api-key <YOUR_API_KEY> [-o output.java]
```

- `--api-key`：Your DeepSeek API Key
- `-o`：Optional，output file name

## Formatting

Jenjoy will use Vim to auto-format your Java file if Vim is available in your system.  
If Vim is not installed, formatting will be skipped and a warning will be shown.

You can also format any file manually:

```sh
python format.py <yourfile.java>
```

## Notes

- Requires network access to the DeepSeek API server.
- Only methods/classes without existing doc comments will be processed.
- Formatting uses Vim with 4-space tabs and auto-indent.

## License

GPLv3
