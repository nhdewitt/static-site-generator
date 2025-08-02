# Static Site Generator

A lightweight static site generator built in Python that converts Markdown content into HTML pages. View the [live demo](https://nhdewitt.github.io/static-site-generator/).

## Features

- Converts Markdown files to styled HTML pages
- Supports common Markdown syntax:
  - Headers (H1-H6)
  - Bold and italic text
  - Code blocks with syntax highlighting
  - Blockquotes
  - Ordered and unordered lists
  - Links and images
- Custom HTML template system
- Automatic navigation between pages
- Clean, responsive design with custom CSS styling
- Preserves directory structure from content to output

## Usage

1. Place your Markdown content files in the `content/` directory
2. Add any static assets (images, CSS) to the `static/` directory
3. Build the site:

```bash
./build.sh
```

This will:

1. Copy static assets to the `docs/` directory
2. Convert all Markdown files to HTML
3. Generate the complete site structure

To run the test suite:

```bash
./test.sh
```

To preview locally:

```bash
./main.sh
```

Then visit `http://localhost:8888`

## Development

This generator is build with Python as part of the [Boot Dev](https://boot.dev) Backend Path (the Guided Project **Build a Static Site Generator in Python**) and includes:

- Markdown parsing and HTML generation
- Custom text node system for inline formatting
- Template variable replacement
- File path handling and directory structure preservation
- Comprehensive unit test suite

## Demo

A demonstration of this project is available at [Github Pages](https://nhdewitt.github.io/static-site-generator/).

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).