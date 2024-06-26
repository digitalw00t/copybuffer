#!/usr/bin/env python3

import argparse
from PIL import Image
import pyperclip
import os
import sys
import tempfile
import subprocess
import shutil
import tiktoken

__VERSION__ = "v1.0-4-ged68b6e"

def is_xclip_installed():
    return shutil.which("xclip") is not None

def is_xsel_installed():
    return shutil.which("xsel") is not None

def is_pyperclip_installed():
    try:
        import pyperclip
        return True
    except ImportError:
        return False

def check_dependencies():
    missing_dependencies = []

    if not is_xclip_installed() and not is_xsel_installed():
        missing_dependencies.append("xclip or xsel")

    if not is_pyperclip_installed():
        missing_dependencies.append("pyperclip")

    return missing_dependencies

def install_dependencies():
    print("Please install the following dependencies:")
    dependencies = check_dependencies()
    for dep in dependencies:
        print(f"- {dep}")

def copy_image_to_clipboard(image_path):
    if not is_xclip_installed():
        print("Error: xclip is not installed. Please install it using 'sudo apt-get install xclip'.")
        return False

    try:
        # Open the image
        image = Image.open(image_path)

        # If it's a GIF, take the first frame and convert to RGB
        if image_path.lower().endswith('.gif'):
            image = image.convert('RGB')

        # Create a temporary file to hold the image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_path = temp_file.name

        # Save the image to the temporary file
        image.save(temp_path)

        # Use xclip to copy the image to the clipboard
        command = f"xclip -selection clipboard -t image/png -i {temp_path}"
        subprocess.run(command, shell=True)

        return True
    except Exception as e:
        print(f"Error: An unexpected error occurred while copying the image. {str(e)}")
        return False

def count_tokens(file_content, encoding_name):
    """
    Count the number of tokens in the given file content using the specified encoding.

    Parameters:
    file_content (str): The contents of the file.
    encoding_name (str): The name of the encoding to be used.

    Returns:
    int: The number of tokens.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(file_content)
    return len(tokens)

def copy_file_contents_to_clipboard(file_contents, include_header=False, discord_attachment=False, file_path=None):
    try:
        if include_header and file_path:
            header = f"=== File: {file_path} ===\n"
            file_contents = header + file_contents

        if discord_attachment and file_path:
            file_contents = f"[Attached file: {file_path}\nContent:\n```\n{file_contents}\n```\n]"

        pyperclip.copy(file_contents)
        return True
    except Exception as e:
        print(f"Error: An unexpected error occurred. {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Copy file contents or images to clipboard.")
    parser.add_argument("--version", action="store_true", help="Display the application version.")
    parser.add_argument("--header", action="store_true", help="Include header for text files.")
    parser.add_argument("-a", "--attachment", action="store_true", help="Format output as Discord attachment.")
    parser.add_argument("-t", "--token", action="store_true", help="Display token count using Tiktoken")
    parser.add_argument("file_paths", metavar='N', nargs='*', help="Paths of the files or images to copy.")
    args = parser.parse_args()

    # Check dependencies before proceeding
    missing_dependencies = check_dependencies()
    if missing_dependencies:
        print("Missing dependencies:")
        for dep in missing_dependencies:
            print(f"- {dep}")
        install_dependencies()
        return

    if args.version:
        print(f"This is the CopyBuffer application, version {__VERSION__}")
        return

    encoding = "cl100k_base"

    if not args.file_paths or '-' in args.file_paths:
        file_content = sys.stdin.read().strip()
        if args.token:
            token_count = count_tokens(file_content, encoding)
            print(f'STDIN contains {token_count} tokens.')
        copy_successful = copy_file_contents_to_clipboard(file_content, args.header, args.attachment)
        if copy_successful:
            print("STDIN copied to the clipboard successfully!")
    else:
        for file_path in args.file_paths:
            print(f"Processing file: {file_path}")  # Debug print
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                copy_successful = copy_image_to_clipboard(file_path)
            else:
                try:
                    with open(file_path, 'r') as file:
                        file_content = file.read().strip()
                        if args.token:
                            token_count = count_tokens(file_content, encoding)
                            print(f'{file_path} contains {token_count} tokens.')
                        copy_successful = copy_file_contents_to_clipboard(file_content, args.header, args.attachment, file_path)
                except FileNotFoundError:
                    print(f"Error: File '{file_path}' not found.")
                    continue

            if copy_successful:
                print(f"{file_path} copied to the clipboard successfully!")

if __name__ == '__main__':
    main()

