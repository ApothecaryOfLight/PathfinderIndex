import sqlite3
import PyPDF2
import PyQt5.QtWidgets as qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
import subprocess

# Step 3: Query database
def search_terms(query, db_path="PathfinderDatabase.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM terms WHERE term LIKE ?", (f"%{query}%",))
    results = cur.fetchall()
    conn.close()
    return results

# Step 4: Open PDF at specific page
def open_pdf(path, page):
    subprocess.run(["qpdfview", f"{path}#{page}"])

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

        # Connect the itemClicked signal to a handler
        self.results_list.itemClicked.connect(self.open_selected_pdf)

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
            item_text = f"Page {result[2]}: {result[3]}"
            item = QListWidgetItem(item_text)
            
            # Store file path and page number as metadata in the item
            item.setData(Qt.UserRole, (result[2], result[3]))
            self.results_list.addItem(item)

    def open_selected_pdf(self, item):
        # Retrieve the file path and page number from the clicked item
        file_path, page_number = item.data(Qt.UserRole)
        
        # Call the open_pdf function with the extracted data
        open_pdf(file_path, page_number)

app = qt.QApplication([])
window = PDFSearchApp()
window.show()
app.exec()

