import os
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_text_from_epub(epub_path, output_txt_path):
    """
    Extracts all text content from an EPUB file and saves it to a .txt file.

    :param epub_path: Path to the input EPUB file.
    :param output_txt_path: Path to save the extracted text as a .txt file.
    """
    try:
        # Open the EPUB file
        book = epub.read_epub(epub_path)
        
        # Initialize an empty string to hold the extracted text
        full_text = ""

        # Iterate through all items in the EPUB
        for item in book.get_items():
            print(f"Processing item: {item.get_name()} (Type: {item.get_type()})")
            
            # Check if the item is of type XHTML or HTML (text-based content)
            if item.get_type() == 'text':  # Corrected condition
                try:
                    # Decode the content and parse it with BeautifulSoup
                    content = item.get_content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract text from the parsed HTML
                    text = soup.get_text(separator='\n')
                    
                    # Append the extracted text to the full_text string
                    full_text += text + "\n\n"  # Add some spacing between sections
                except Exception as e:
                    print(f"Error parsing item {item.get_name()}: {e}")

        # Write the extracted text to the output .txt file
        if full_text.strip():  # Only write if there's actual content
            with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(full_text)
            print(f"Text extracted from {epub_path} and saved to {output_txt_path}")
        else:
            print(f"No text content found in {epub_path}. Skipping...")
    
    except Exception as e:
        print(f"Failed to process {epub_path}: {e}")

def process_epub_folder(input_folder, output_folder):
    """
    Processes all EPUB files in the input folder and saves the extracted text into separate .txt files.

    :param input_folder: Path to the folder containing EPUB files.
    :param output_folder: Path to the folder where the extracted text files will be saved.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".epub"):
            # Construct full file paths
            epub_path = os.path.join(input_folder, filename)
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            output_txt_path = os.path.join(output_folder, txt_filename)

            # Extract text from the EPUB and save it to a .txt file
            extract_text_from_epub(epub_path, output_txt_path)

if __name__ == "__main__":
    # Folder containing EPUB files
    input_folder = "epub_to_parse"
    
    # Folder to save the extracted text files
    output_folder = "epub_in_txt"
    
    # Process all EPUB files in the input folder
    process_epub_folder(input_folder, output_folder)

    print("All EPUB files have been processed.")