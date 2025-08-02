from markdown_extract import extract_title
from markdown_to_html_node import markdown_to_html_node

import os


def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    dest_dir = os.path.dirname(dest_path)
    
    with open(from_path) as f:
        md_file = f.read()
    with open(template_path) as f:
        template_file = f.read()
    
    html = markdown_to_html_node(md_file).to_html()
    title = extract_title(md_file)

    template_file = template_file.replace("{{ Title }}", title)
    template_file = template_file.replace("{{ Content }}", html)

    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, 'w') as w:
        w.write(template_file)