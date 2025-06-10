import sys
import json
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QMenu, QLabel  # Add QLabel here
)
from PyQt6.QtGui import QPalette, QColor, QAction, QMovie  # Add QMovie here
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal  # Add QTimer, QThread, pyqtSignal import

from scraper_1337x import search_1337x, get_magnet_link
from scraper_jackett import search_jackett
from premiumize_api import PremiumizeClient, load_or_prompt_token

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SearchThread(QThread):
    search_finished = pyqtSignal(list)  # Signal to emit search results

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            logging.debug(f"Starting search for query: {self.query}")
            #results_1337x = search_1337x(self.query)
            results_1337x = []  # Placeholder for 1337x results
            #remove the comment to enable 1337x search
            results_jackett = search_jackett(self.query)
            results = results_jackett  # Use Jackett results for now

            logging.debug(f"Search completed. Found {len(results)} results (1337x: {len(results_1337x)}, Jackett: {len(results_jackett)}).")
            self.search_finished.emit(results)
        except Exception as e:
            logging.error(f"Error during search: {e}", exc_info=True)
            self.search_finished.emit([])  # Emit empty results on error


class TorrentSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ploof Torrent Search")
        self.resize(800, 600)

        self.api = PremiumizeClient()

        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)

        input_layout.addWidget(self.search_bar)
        input_layout.addWidget(self.search_btn)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Title", "Seeders", "Leechers", "Magnet Link", "URL"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)

        self.send_btn = QPushButton("Send to Premiumize")
        self.send_btn.clicked.connect(self.send_selected)

        layout.addLayout(input_layout)
        layout.addWidget(self.results_table)
        layout.addWidget(self.send_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for updating the search button text with scrolling dots
        self.searching_timer = QTimer()
        self.searching_timer.timeout.connect(self.update_search_button_text)
        self.searching_dots = 0  # Counter for the scrolling dots

        # Connect the Enter key to trigger the search
        self.search_bar.returnPressed.connect(self.perform_search)

    def perform_search(self):
        query = self.search_bar.text().strip()
        if not query:
            QMessageBox.warning(self, "Error", "Please enter a search term.")
            return

        # Disable the search button and start the timer for scrolling dots
        self.search_btn.setEnabled(False)
        self.searching_dots = 0
        self.searching_timer.start(500)  # Update every 500ms

        # Start the search in a separate thread
        self.search_thread = SearchThread(query)
        self.search_thread.search_finished.connect(self.on_search_finished)
        self.search_thread.start()

    def update_search_button_text(self):
        # Update the search button text with scrolling dots
        dots = "." * self.searching_dots
        self.search_btn.setText(f"Searching{dots}")
        self.searching_dots = (self.searching_dots + 1) % 4  # Cycle through 0, 1, 2, 3 dots

    def on_search_finished(self, results):
        # Populate the results table
        self.results_table.setRowCount(len(results))
        for row, (title, seeders, leechers, magnet_link, url) in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(title))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(seeders)))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(leechers)))

            magnet_item = QTableWidgetItem(magnet_link)
            magnet_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.results_table.setItem(row, 3, magnet_item)

            url_item = QTableWidgetItem(url)
            url_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.results_table.setItem(row, 4, url_item)

        # Re-enable the search button, stop the timer, and reset the button text
        self.searching_timer.stop()
        self.search_btn.setText("Search")
        self.search_btn.setEnabled(True)

    def send_selected(self):
        row = self.results_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a torrent.")
            return
        title = self.results_table.item(row, 0).text()
        url = self.results_table.item(row, 4).text()  # Updated to get URL from the correct column
        magnet = get_magnet_link(url)
        if not magnet:
            QMessageBox.critical(self, "Error", "Failed to retrieve magnet link.")
            return
        success = self.api.send_magnet(magnet)
        if success:
            QMessageBox.information(self, "Success", f"Sent '{title}' to Premiumize.")
        else:
            QMessageBox.critical(self, "Error", "Failed to send to Premiumize.")

    def show_context_menu(self, position):
        menu = QMenu()
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selected_cell)
        menu.addAction(copy_action)
        menu.exec(self.results_table.viewport().mapToGlobal(position))

    def copy_selected_cell(self):
        selected_item = self.results_table.currentItem()
        if selected_item:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_item.text())

def apply_dark_theme(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    app.setStyle("Fusion")
    app.setPalette(dark_palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_or_prompt_token()  # Moved here, after QApplication is created
    apply_dark_theme(app)
    window = TorrentSearchApp()
    window.show()
    sys.exit(app.exec())
