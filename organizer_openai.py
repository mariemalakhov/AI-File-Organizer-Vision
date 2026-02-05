import os
import shutil
import time
import base64
from openai import OpenAI
import fitz 
from docx import Document
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Using environment variables so my API key isn't exposed on GitHub
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "AI_Project")
INPUT_DIR = os.path.join(BASE_DIR, "Input_Files")
OUTPUT_DIR = os.path.join(BASE_DIR, "Organized_Files")

client = OpenAI(api_key=API_KEY)
# Helper to turn images into something the Vision API can read
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_ai_decision(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    
# Simple instructions for the AI to keep the output consistent
    prompt_text = "Analyze this file. Categorize as University, Career, Personal, or Finance. Pick a Subfolder (e.g., Calculus, IBM, Receipts). Create a New Name: YYYY-MM-DD_Subject. Respond ONLY as: Category|Subfolder|NewName"

    try:
        if ext in [".jpg", ".png", ".jpeg"]:
           # Use gpt-4o-mini's vision capabilities for screenshots/images
            base64_image = encode_image(file_path)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ]
            )
        else:
          # For documents, just grab the first chunk of text to save on tokens
            content = ""
            if ext == ".pdf":
                with fitz.open(file_path) as doc: content = doc[0].get_text()[:2000]
            elif ext == ".docx":
                doc = Document(file_path)
                content = "\n".join([p.text for p in doc.paragraphs[:20]])
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"{prompt_text}\nContent: {content}\nFilename: {filename}"}]
            )

        # Ensure the response follows the Category|Subfolder|Name format
        result = response.choices[0].message.content.strip()
        return result if "|" in result else "Personal|Unsorted|Manual_Review"
    except Exception as e:
        print(f"Error: {e}")
        return "Personal|Unsorted|Error_File"

def process_file(file_path):
    filename = os.path.basename(file_path)
    # Ignore hidden system files or accidentally dropped folders
    if filename.startswith('.') or os.path.isdir(file_path): return
    
    print(f"Analyzing: {filename}")
    # Sleep for 2s to make sure the file is fully written to disk before touched
    time.sleep(2) 
    
    decision = get_ai_decision(file_path)
    category, subfolder, new_name = decision.split('|')

    final_dir = os.path.join(OUTPUT_DIR, category, subfolder)
    os.makedirs(final_dir, exist_ok=True)
    
    ext = os.path.splitext(filename)[1]
    dest_path = os.path.join(final_dir, f"{new_name}{ext}")
    # Copy then Delete strategy to avoid issues with Windows file locks

    shutil.copy(file_path, dest_path)
    try:
        os.remove(file_path)
        print(f"Moved to: {category}/{subfolder}")
    except:
        print(f"Original locked, but copy created in {category}.")

class Handler(FileSystemEventHandler):
    # This triggers as soon as a file is dropped into the input folder
    def on_created(self, event):
        if not event.is_directory: process_file(event.src_path)

if __name__ == "__main__":
    # Set up folder structure on startup
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Start the observer to watch the input directory
    observer = Observer()
    observer.schedule(Handler(), INPUT_DIR, recursive=False)
    observer.start()
    print("Auto-Organizer with VISION is ACTIVE.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
