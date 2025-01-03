import sqlite3
import PyPDF2
import re
import PyQt5.QtWidgets as qt
import subprocess

# Step 1: Extract data from PDFs
def extract_terms_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        terms = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            # Find capitalized words or phrases
            matches = re.findall(r'[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*', text)
            for match in matches:
                terms.append({"term": match, "page": page_number, "context": text, "file": file_path})
    return terms

# Step 2: Save to SQLite database
def save_to_database(terms, db_path="documents.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS terms (
                    id INTEGER PRIMARY KEY,
                    term TEXT,
                    document_path TEXT,
                    page_number INTEGER,
                    context_snippet TEXT)""")
    for term in terms:
        cur.execute("INSERT INTO terms (term, document_path, page_number, context_snippet) VALUES (?, ?, ?, ?)",
                    (term["term"], term["file"], term["page"], term["context"]))
    conn.commit()
    conn.close()

def process_pdf(path):
  items = extract_terms_from_pdf(path)
  save_to_database(items)

# Step 3: Query database
def search_terms(query, db_path="documents.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM terms WHERE term LIKE ?", (f"%{query}%",))
    results = cur.fetchall()
    conn.close()
    return results

# Step 4: Open PDF at specific page
def open_pdf(path, page):
    subprocess.run(["evince", f"--page-label={page}", path])

# Step 5: GUI for searching and previewing
class PDFSearchApp(qt.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.search_box = qt.QLineEdit(self)
        self.results_list = qt.QListWidget(self)
        self.search_button = qt.QPushButton("Search", self)
        self.search_button.clicked.connect(self.search)

        layout = qt.QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_list)
        self.setLayout(layout)
        self.setWindowTitle("PDF Search")
        self.resize(800, 600)

    def search(self):
        query = self.search_box.text()
        results = search_terms(query)
        self.results_list.clear()
        for result in results:
            self.results_list.addItem(f"{result[1]} - Page {result[2]}: {result[3]}")

process_pdf("./data/PZO9279 Andoran, Birthplace of Freedom.pdf")
process_pdf("./data/PZO1111 Campaign Setting.pdf")
app = qt.QApplication([])
window = PDFSearchApp()
window.show()
app.exec()

