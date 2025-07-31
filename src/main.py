from textnode import TextNode, TextType

def main():
    tn = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(tn)

if __name__ == "__main__":
    main()