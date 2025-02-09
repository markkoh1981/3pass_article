import os
import wikipediaapi
import ollama

# Step 1: Set up directories
def setup_directories():
    if not os.path.exists("inputs"):
        os.makedirs("inputs")

# Step 2: Fetch data from Wikipedia including references
def fetch_wikipedia_data(topic):
    # Specify a custom user agent as per Wikipedia's policy
    user_agent = "ResearchModule/1.0 (https://www.vxglobal.sg; mark@vxglobal.sg)"
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent=user_agent
    )
    
    page = wiki_wiki.page(topic)
    
    if page.exists():
        # Extract summary
        summary = page.summary
        
        # Extract references
        references = []
        sections = page.sections
        for section in sections:
            if section.title.lower() == "references":
                for reference in section.text.split("\n"):
                    if reference.strip():  # Ignore empty lines
                        references.append(reference.strip())
        
        return {
            "summary": summary,
            "url": page.fullurl,
            "references": references
        }
    else:
        return None

# Step 3: Format references in APA style
def format_references_in_apa(references):
    formatted_references = []
    for ref in references:
        # Basic formatting for APA (this is simplified; real APA requires more parsing)
        if "[" in ref and "]" in ref:
            citation = ref.split("]", 1)[1].strip()
        else:
            citation = ref.strip()
        formatted_references.append(citation)
    return formatted_references

# Step 4: Save research data to a text file
def save_research_to_file(topic, wikipedia_data):
    # Sanitize the topic to create a valid file name
    sanitized_topic = sanitize_topic(topic)
    file_path = os.path.join("inputs", f"{sanitized_topic}.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"Research on: {topic}\n\n")
        
        if wikipedia_data:
            file.write("Wikipedia Summary:\n")
            file.write(wikipedia_data["summary"] + "\n")
            file.write(f"Source: {wikipedia_data['url']}\n\n")
            
            if wikipedia_data["references"]:
                file.write("References (APA Style):\n")
                formatted_references = format_references_in_apa(wikipedia_data["references"])
                for idx, ref in enumerate(formatted_references, start=1):
                    file.write(f"{idx}. {ref}\n")
            else:
                file.write("No references found.\n\n")
        else:
            file.write("No Wikipedia data found.\n")

# Sanitize the topic to create a valid file name
def sanitize_topic(topic):
    # Remove invalid characters and replace spaces with underscores
    sanitized = topic.strip().split("\n")[0]  # Take only the first line
    sanitized = sanitized.replace(" ", "_")  # Replace spaces with underscores
    sanitized = "".join(char for char in sanitized if char.isalnum() or char in "_-")  # Keep only alphanumeric and safe characters
    return sanitized

# Interpret the topic using Ollama AI Llama3.2:8b
def interpret_topic_with_ollama(topic):
    try:
        response = ollama.chat(
            model="llama3.2:latest",  # Replace with your actual model name
            messages=[
                {"role": "system", "content": "You are an academic research assistant."},
                {"role": "user", "content": f"Interpret the following topic as it would appear on Wikipedia: {topic}. Do not return any explanation, just the reworded topic."}
            ]
        )
        interpretation = response['message']['content'].strip()
        return interpretation
    except Exception as e:
        print(f"Error interpreting topic with Ollama: {e}")
        return topic  # Fallback to the original topic if interpretation fails

# Step 5: Main function to orchestrate the research process
def conduct_research(topic):
    setup_directories()
    
    print(f"Conducting research on: {topic}")
    
    # Interpret the topic using Ollama AI
    interpreted_topic = interpret_topic_with_ollama(topic)
    print(f"Interpreted topic: {interpreted_topic}")
    
    # Fetch Wikipedia data
    wikipedia_data = fetch_wikipedia_data(interpreted_topic)
    
    # Save the research data to a file
    save_research_to_file(interpreted_topic, wikipedia_data)
    print(f"Research saved to inputs/{sanitize_topic(interpreted_topic)}.txt")

# Example usage
if __name__ == "__main__":
    topic = input("Enter the research topic: ").strip()
    conduct_research(topic)