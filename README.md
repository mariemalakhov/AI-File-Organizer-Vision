Why I Built This
My desktop was constantly cluttered with files like "Screenshot 2025-09-04..." and unsorted PDFs from my classes at Montclair State. I needed a way to organize my academic materials, specifically for Data Structures/Algorithms and Calculus II, without spending hours manually renaming files. I built this tool to act as a "smart assistant" that actually looks at what's inside a file before deciding where it goes.

Key Decisions
Why Vision? Standard automation scripts usually fail on screenshots because there is no selectable text. By integrating the GPT-4o Vision API, I enabled the script to "see" the content of images and categorize them accurately.

Security: I transitioned from hard coded API keys to using Environment Variables. This keeps my credentials safe while allowing the code to be public and portable.

Handling OS Locks: I ran into issues where Windows would lock files during the moving process. I solved this by implementing a "Copy-then-Delete" sequence to ensure data integrity.

How It Works
Watch: The script monitors my "Input_Files" folder in real time.

Read: It uses Python libraries to extract text from PDFs/Docs or encodes images for the Vision API.

Sort: The AI determines the category (University, Career, Finance, etc.) and a subfolder based on the subject matter.

Clean: It renames the file to a standard YYYY-MM-DD format and moves it to the organized directory.

Future Roadmap
Add a duplicate detection system to save storage.

Build a simple GUI so I don't have to keep a terminal window open.

Integrate character recognition for my language homework.