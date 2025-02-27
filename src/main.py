from textnode import TextNode, TextType

def main():
	NewObject = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")

	print(NewObject)

main()
