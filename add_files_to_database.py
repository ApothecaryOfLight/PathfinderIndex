import sqlite3
import PyPDF2
import re

# Step 1: Extract data from PDFs
def extract_terms_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        terms = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            print(text)
            # Find capitalized words or phrases
            matches = re.findall(r'[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*', text)
            for match in matches:
                terms.append({"term": match, "page": page_number, "file": file_path})
    return terms

# Step 2: Save to SQLite database
def save_to_database(terms, db_path="PathfinderDatabase.db"):
    print("Adding to SQL database...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS terms (
                    id INTEGER PRIMARY KEY,
                    term TEXT,
                    document_path TEXT,
                    page_number INTEGER,
                    context_snippet TEXT)""")
    for term in terms:
        cur.execute("INSERT INTO terms (term, document_path, page_number) VALUES (?, ?, ?)",
                    (term["term"], term["file"], term["page"]))
    conn.commit()
    conn.close()

def process_pdf(path):
  print(f"Processing {path}!")
  items = extract_terms_from_pdf(path)
  save_to_database(items)

#process_pdf("./data/Advanced Class Guide (2nd Printing).pdf")
#process_pdf("./data/Advanced Player's Guide (2nd Printing).pdf")
#process_pdf("./data/Advanced Race Guide (2nd Printing).pdf")
#process_pdf("./data/Adventurers Guide.pdf")
#process_pdf("./data/GameMastery Guide (3rd printing).pdf")
#process_pdf("./data/Pathfinder RPG - Core Rulebook (6th Printing).pdf")
process_pdf("./data/PZO9226 Inner Sea World Guide.pdf")
