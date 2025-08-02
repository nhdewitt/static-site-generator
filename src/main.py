import os

from get_file_paths import get_file_paths
from static_to_public import copy_source_dir_to_destination_dir
from markdown_generate import generate_page

STATIC_PATH = "./static"
PUBLIC_PATH = "./public"
CONTENT_PATH = "./content"
TEMPLATE_PATH = "./template.html"

def main():
    copy_source_dir_to_destination_dir(STATIC_PATH, PUBLIC_PATH)
    content_files = get_file_paths(CONTENT_PATH)
    for content in content_files:
        relative_path = os.path.relpath(content, "content")
        html_path = relative_path.replace(".md", ".html")
        output_path = os.path.join(PUBLIC_PATH, html_path)
        generate_page(content, TEMPLATE_PATH, output_path)

if __name__ == "__main__":
    main()