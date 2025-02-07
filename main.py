import os
import ollama
import datetime
from pdfreader import SimplePDFViewer

def get_document_content(filename):
    """Get content of a document from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

def extract_text(content):
    """Extract and clean text from the document."""
    try:
        extracted_text = content.replace('\n', ' ')
        extracted_text = extracted_text.lower().replace('—', ', ').replace('---', '.').replace('--', '-')
        return extracted_text
    except Exception as e:
        raise ValueError(f"Error extracting text: {e}")

def pass_1_article_generation(text):
    """Generate a readable article from the input text."""
    try:
        response = ollama.chat(
            model="llama3.2:latest",  # Replace with your actual model name
            messages=[
                {"role": "system", "content": "You are an expert writer skilled in rewording press releases into articles."},
                {"role": "user", "content": f"Please reword this press release into a readable article for a reputable site with quotes weaved in with more than 350 words, formatted in British spelling, and a newsletter-friendly title that is SEO friendly in under 60 characters:\n{text}"}
            ]
        )
        return response['message']['content']
    except Exception as e:
        raise ValueError(f"Error in Pass 1 (article generation): {e}")

def pass_2_title_generation(text):
    """Generate SEO-friendly titles for the article."""
    try:
        response = ollama.chat(
            model="llama3.2:latest",  # Replace with your actual model name
            messages=[
                {"role": "system", "content": "You are an SEO expert skilled in crafting engaging titles."},
                {"role": "user", "content": f"Please summarise this press release and give 10 examples of an SEO friendly title under 60 characters:\n{text}"}
            ]
        )
        return response['message']['content']
    except Exception as e:
        raise ValueError(f"Error in Pass 2 (title generation): {e}")

def pass_3_meta_description_generation(text):
    """Generate meta descriptions for the article."""
    try:
        response = ollama.chat(
            model="llama3.2:latest",  # Replace with your actual model name
            messages=[
                {"role": "system", "content": "You are an SEO expert skilled in crafting concise meta descriptions."},
                {"role": "user", "content": f"Please summarise this press release and give 10 examples of a meta description under 140 characters:\n{text}"}
            ]
        )
        return response['message']['content']
    except Exception as e:
        raise ValueError(f"Error in Pass 3 (meta description generation): {e}")

def save_output(output_content, output_type, project_name, directory):
    """Save the output content to a file in the specified directory with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(directory, f"{project_name}_{output_type}_{timestamp}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output_content)
    print(f"{output_type.capitalize()} saved to {filename}")

def create_output_directory(project_name):
    """Create a directory for saving outputs."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    directory = os.path.join("outputs", f"{project_name}_{timestamp}")
    os.makedirs(directory, exist_ok=True)
    return directory

def process_files_in_directory(directory):
    """Process all files in the input directory and generate outputs for each."""
    processed_files = set()
    if os.path.exists("processed_files.txt"):
        with open("processed_files.txt", 'r', encoding='utf-8') as f:
            processed_files = set(f.read().splitlines())
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.pdf') or filename.endswith('.txt'):
            if filename not in processed_files:
                try:
                    content = get_pdf_content(file_path)
                    text = extract_text(content)
                    project_name = os.path.splitext(filename)[0]
                    output_directory = create_output_directory(project_name)
                    
                    # Pass 1: Generate the article
                    article = pass_1_article_generation(text)
                    save_output(article, "article", project_name, output_directory)
                    
                    # Pass 2: Generate SEO-friendly titles
                    titles = pass_2_title_generation(text)
                    save_output(titles, "titles", project_name, output_directory)
                    
                    # Pass 3: Generate meta descriptions
                    meta_descriptions = pass_3_meta_description_generation(text)
                    save_output(meta_descriptions, "meta_descriptions", project_name, output_directory)
                    
                    # Mark the file as processed
                    with open("processed_files.txt", 'a', encoding='utf-8') as f:
                        f.write(filename + "\n")
                    print(f"Outputs for {filename} saved.")
                except Exception as e:
                    print(f"An error occurred while processing {filename}: {e}")
            else:
                print(f"Outputs for {filename} already exist. Skipping.")

def get_pdf_content(file_path):
    """Extract text content from a PDF file or read directly if it's a .txt file."""
    try:
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            with open(file_path, 'rb') as f:
                viewer = SimplePDFViewer(f)
                text = ""
                for canvas in viewer:
                    viewer.render()
                    text += " ".join(viewer.canvas.strings) + "\n"
                return text
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

def main():
    input_directory = "input"
    if not os.path.exists(input_directory):
        print(f"Input directory '{input_directory}' does not exist.")
        return
    process_files_in_directory(input_directory)
    print("All files processed.")

if __name__ == "__main__":
    main()