import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTextEdit, 
                             QLabel, QScrollArea, QFrame, QSpinBox, QTabWidget,
                             QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import time

# Import RAG Engine (asigură-te că rag_engine.py există)
try:
    from rag_engine import RAGEngine
except ImportError:
    RAGEngine = None

# ============================================================================
# WORKERS (THREADS)
# ============================================================================

class SearchWorker(QThread):
    """Thread pentru căutare documente"""
    finished = pyqtSignal(list, float)
    error = pyqtSignal(str)
    
    def __init__(self, client, model, query, limit):
        super().__init__()
        self.client = client
        self.model = model
        self.query = query
        self.limit = limit
        
    def run(self):
        try:
            start_time = time.time()
            query_vector = self.model.encode(self.query).tolist()
            
            results = self.client.query_points(
                collection_name="documente_pdf",
                query=query_vector,
                limit=self.limit
            ).points
            
            duration = time.time() - start_time
            self.finished.emit(results, duration)
        except Exception as e:
            self.error.emit(str(e))

class ChatWorker(QThread):
    """Thread pentru chat cu LLM"""
    finished = pyqtSignal(str, list)
    error = pyqtSignal(str)
    
    def __init__(self, client, model, rag_engine, query):
        super().__init__()
        self.client = client
        self.model = model
        self.rag_engine = rag_engine
        self.query = query
        
    def run(self):
        try:
            # 1. Retrieval (Căutare context)
            query_vector = self.model.encode(self.query).tolist()
            results = self.client.query_points(
                collection_name="documente_pdf",
                query=query_vector,
                limit=5
            ).points
            
            context_chunks = [r.payload for r in results]
            
            # 2. Generation (LLM)
            if self.rag_engine:
                answer = self.rag_engine.genereaza_raspuns(self.query, context_chunks)
            else:
                answer = "Eroare: RAG Engine nu este disponibil (instalează 'openai' sau verifică 'rag_engine.py')."
            
            self.finished.emit(answer, results)
            
        except Exception as e:
            self.error.emit(str(e))

# ============================================================================
# WIDGETS UI
# ============================================================================

class ResultCard(QFrame):
    """Card pentru afișarea unui rezultat în lista de căutare"""
    def __init__(self, result, index):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #e2e8f0;
            }
            QFrame:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        score_label = QLabel(f"#{index + 1} • Scor: {result.score:.4f}")
        score_label.setStyleSheet("color: #2563eb; font-weight: bold;")
        header.addWidget(score_label)
        header.addStretch()
        
        source = os.path.basename(result.payload.get('sursa_fisier', 'N/A'))
        page = result.payload.get('pagina', 'N/A')
        doc_type = result.payload.get('tip_document', 'DOC')
        
        source_label = QLabel(f"[{doc_type}] {source} • Pagina {page}")
        source_label.setStyleSheet("color: #64748b; font-size: 12px;")
        header.addWidget(source_label)
        layout.addLayout(header)
        
        # Text
        text = result.payload.get('text_chunk', '')
        text_label = QLabel(text[:400] + ('...' if len(text) > 400 else ''))
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: #334155; margin-top: 8px; line-height: 1.4;")
        layout.addWidget(text_label)
        
        self.setLayout(layout)

class SearchTab(QWidget):
    """Tab-ul 1: Căutare Clasică"""
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search Bar Area
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Caută în documente...")
        self.search_input.setStyleSheet("""
            QLineEdit { padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px; }
            QLineEdit:focus { border-color: #2563eb; }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input, stretch=4)
        
        self.limit_spinner = QSpinBox()
        self.limit_spinner.setRange(1, 50)
        self.limit_spinner.setValue(10)
        self.limit_spinner.setStyleSheet("QSpinBox { padding: 8px; border: 2px solid #e2e8f0; border-radius: 8px; }")
        search_layout.addWidget(self.limit_spinner)
        
        self.search_btn = QPushButton("🔍 Caută")
        self.search_btn.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Status
        self.status_label = QLabel("Gata de căutare")
        self.status_label.setStyleSheet("color: #64748b; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Results Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.addStretch()
        
        scroll.setWidget(self.results_widget)
        layout.addWidget(scroll)
        
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query: return
        
        self.search_btn.setEnabled(False)
        self.status_label.setText("🔍 Se caută...")
        
        # Clear results
        while self.results_layout.count() > 1:
            child = self.results_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        # Start worker
        self.worker = SearchWorker(
            self.parent_window.client,
            self.parent_window.model,
            query,
            self.limit_spinner.value()
        )
        self.worker.finished.connect(self.display_results)
        self.worker.error.connect(self.display_error)
        self.worker.start()
        
    def display_results(self, results, duration):
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"✅ {len(results)} rezultate în {duration:.2f}s")
        
        for i, result in enumerate(results):
            card = ResultCard(result, i)
            self.results_layout.insertWidget(i, card)
            
    def display_error(self, msg):
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"❌ Eroare: {msg}")

class ChatTab(QWidget):
    """Tab-ul 2: Chat cu AI"""
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Chat History
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Input Area
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Întreabă AI-ul despre documente...")
        self.chat_input.setStyleSheet("""
            QLineEdit { padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 14px; }
            QLineEdit:focus { border-color: #8b5cf6; }
        """)
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        
        self.send_btn = QPushButton("Trimite 🚀")
        self.send_btn.setStyleSheet("""
            QPushButton { background-color: #8b5cf6; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Sources Label
        self.sources_label = QLabel("")
        self.sources_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(self.sources_label)
        
    def send_message(self):
        query = self.chat_input.text().strip()
        if not query: return
        
        # Add user message
        self.append_message("Tu", query, "#2563eb")
        self.chat_input.clear()
        self.send_btn.setEnabled(False)
        self.sources_label.setText("🤖 AI-ul gândește și citește documente...")
        
        # Start worker
        self.worker = ChatWorker(
            self.parent_window.client,
            self.parent_window.model,
            self.parent_window.rag_engine,
            query
        )
        self.worker.finished.connect(self.display_response)
        self.worker.error.connect(self.display_error)
        self.worker.start()
        
    def display_response(self, answer, sources):
        self.send_btn.setEnabled(True)
        self.append_message("AI", answer, "#059669")
        
        # Show sources
        source_names = [os.path.basename(r.payload.get('sursa_fisier', '')) for r in sources]
        unique_sources = list(set(source_names))[:3]
        self.sources_label.setText(f"📚 Surse folosite: {', '.join(unique_sources)}")
        
    def display_error(self, msg):
        self.send_btn.setEnabled(True)
        self.append_message("System", f"Eroare: {msg}", "#ef4444")
        
    def append_message(self, sender, text, color):
        self.chat_history.append(f'<b style="color:{color}">{sender}:</b> {text}<br>')

# ============================================================================
# MAIN WINDOW
# ============================================================================

class SearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.model = None
        self.rag_engine = None
        
        self.init_ui()
        self.init_backend()
        
    def init_ui(self):
        self.setWindowTitle("🔍 PyPro Search & Chat")
        self.setGeometry(100, 100, 1100, 800)
        
        # Main Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("PyPro Intelligent Search")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 8px; background: white; }
            QTabBar::tab {
                background: #f1f5f9;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #64748b;
            }
            QTabBar::tab:selected {
                background: white;
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }
        """)
        
        self.search_tab = SearchTab(self)
        self.chat_tab = ChatTab(self)
        
        self.tabs.addTab(self.search_tab, "🔍 Căutare Documente")
        self.tabs.addTab(self.chat_tab, "💬 Chat cu AI")
        
        main_layout.addWidget(self.tabs)
        
        # Status Bar
        self.status_bar = QLabel("Inițializare sistem...")
        self.status_bar.setStyleSheet("padding: 5px; color: #64748b;")
        main_layout.addWidget(self.status_bar)
        
    def init_backend(self):
        """Load models in background"""
        self.status_bar.setText("⏳ Se încarcă modelele AI (poate dura puțin)...")
        QApplication.processEvents()
        
        try:
            # 1. Qdrant
            self.client = QdrantClient(path="qdrant_db")
            
            # 2. Embedding Model
            self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            
            # 3. RAG Engine (Local)
            if RAGEngine:
                try:
                    self.rag_engine = RAGEngine(provider="local", model_name="llama3")
                    rag_status = "✅ RAG Activat"
                except Exception as e:
                    rag_status = "❌ RAG Indisponibil"
                    print(f"RAG Error: {e}")
            else:
                rag_status = "❌ RAG Modul Lipsă"
            
            # Update UI
            info = self.client.get_collection("documente_pdf")
            count = info.points_count
            
            self.status_bar.setText(f"✅ Sistem Gata! {count} documente indexate • {rag_status}")
            self.status_bar.setStyleSheet("color: #059669; font-weight: bold; padding: 5px;")
            
        except Exception as e:
            self.status_bar.setText(f"❌ Eroare Inițializare: {str(e)}")
            self.status_bar.setStyleSheet("color: #ef4444; font-weight: bold; padding: 5px;")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SearchGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
