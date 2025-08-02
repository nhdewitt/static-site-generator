import unittest
from markdown_extract import extract_title
from exceptions import InvalidHTMLError

class TestStaticToPublic(unittest.TestCase):
    def TestExtractTitle(self):
        md = """
# Lorem Ipsum Template

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada.

## Introduction

Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer non lorem sit amet elit faucibus tincidunt.

## Features

- **Responsive**: Lorem ipsum dolor sit amet.
- **Lightweight**: Consectetur adipiscing elit.
- **Customizable**: Nulla vitae elit libero.

## Conclusion

Sed posuere consectetur est at lobortis. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.
"""
        title = extract_title(md)
        self.assertEqual(title, "Lorem Ipsum Template")
    
    def TestHeaderMissing(self):
        md = """
## Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque aliquet quam at urna hendrerit, vitae aliquam purus consequat. Donec vitae nisi vitae urna sollicitudin sollicitudin.

### Background

Phasellus in turpis vitae eros tristique dictum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Mauris nec magna sit amet velit elementum fermentum.

## Main Content

- **Section One**: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
- **Section Two**: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
- **Section Three**: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi.

### Details

1. Curabitur pretium tincidunt lacus.
2. Nulla gravida orci a odio.
3. Nullam varius, turpis et commodo pharetra.

## Conclusion

Vestibulum convallis, lorem a semper suscipit, orci quam aliquet ipsum, nec lacinia dolor mauris eu tortor. Integer sit amet mauris non sapien consequat feugiat.
"""
        with self.assertRaises(InvalidHTMLError):
            title = extract_title(md)

if __name__ == "__main__":
    unittest.main()