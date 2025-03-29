import sys, os, tempfile, cv2, threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread

from src.utils.pdf_processor import PDFProcessor
from src.ui.prompts import construct_prompt
from src.ui.report_generator import generate_markdown_report


class ProcessingWorker(QObject):
    """Worker class for processing PDFs in a background thread"""
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, api_key, pdf_paths, prompt, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.pdf_paths = pdf_paths
        self.prompt = prompt
        
    def run(self):
        try:
            processor = PDFProcessor(self.api_key)
            self.progress.emit(30)
            
            # Process the PDFs and get the API response
            response = processor.process_pdfs(self.pdf_paths, self.prompt)
            self.progress.emit(80)
            
            # Signal success with the response
            self.result.emit(response)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class RisonCopyChecker(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Set application icon
        icon_path = "attached_assets/rison icon.ico"
        self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Set window size based on screen dimensions
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.4)  
        window_height = int(screen.height() * 0.7)
        x = int((screen.width() - window_width) / 2)
        y = int(screen.height() * 0.05)
        self.setGeometry(x, y, window_width, window_height)

        self.setWindowTitle("Rison Copy Checker")
        self.setStyleSheet("background-color: #97F4FC;")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        title_font = QtGui.QFont("Arial", 26, QtGui.QFont.Bold)
        button_font = QtGui.QFont("Arial", 12)
        label_font = QtGui.QFont("Arial", 12)

        title_label = QtWidgets.QLabel("Rison Copy Checker", self)
        title_label.setFont(title_font)
        title_label.setStyleSheet("background-color: #052123; color:#FFFFFF;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Video Background
        video_path = "attached_assets/HDRobotVideo.mp4"
        self.capture = cv2.VideoCapture(video_path)
        
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.video_label.setScaledContents(True)
        video_width = int(window_width)
        video_height = int(window_height * 0.85)
        self.video_label.setFixedSize(video_width, video_height)
        
        # Display the first frame of the video
        ret, frame = self.capture.read()
        if ret:
            # Convert the frame from BGR to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_image))
            # Reset to the first frame
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Create a horizontal layout
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addStretch(1)  # Left spacer
        h_layout.addWidget(self.video_label)
        h_layout.addStretch(1)  # Right spacer
        layout.addLayout(h_layout)
        
        # Timer for updating video frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)  # 20 ms for roughly 30 FPS
        
        # Video playback control
        self.video_playing = False  # Start with video paused

        button_width = int(window_width * 0.6)

        # Question Paper Upload
        question_layout = QtWidgets.QHBoxLayout()
        self.question_paper_upload_button = QtWidgets.QPushButton("Upload the Question Paper PDF", self)
        self.question_paper_upload_button.setFont(button_font)
        self.question_paper_upload_button.setStyleSheet("background-color: #effdfe; color: #000000;")
        self.question_paper_upload_button.setFixedWidth(button_width)
        self.question_paper_upload_button.clicked.connect(self.upload_question_pdf)
        question_layout.addWidget(self.question_paper_upload_button)
        self.question_status_label = QtWidgets.QLabel("No file selected", self)
        self.question_status_label.setFont(label_font)
        self.question_status_label.setStyleSheet("color: #000000;")
        question_layout.addWidget(self.question_status_label)
        layout.addLayout(question_layout)

        # Answer Sheet Upload
        answer_layout = QtWidgets.QHBoxLayout()
        self.answer_sheet_upload_button = QtWidgets.QPushButton("Upload the Answer Sheet PDF", self)
        self.answer_sheet_upload_button.setFont(button_font)
        self.answer_sheet_upload_button.setStyleSheet("background-color: #effdfe; color: #000000;")
        self.answer_sheet_upload_button.setFixedWidth(button_width)
        self.answer_sheet_upload_button.clicked.connect(self.upload_answer_pdf)
        answer_layout.addWidget(self.answer_sheet_upload_button)
        self.answer_status_label = QtWidgets.QLabel("No file selected", self)
        self.answer_status_label.setFont(label_font)
        self.answer_status_label.setStyleSheet("color: #000000;")
        answer_layout.addWidget(self.answer_status_label)
        layout.addLayout(answer_layout)

        # Reference Answer Sheet Upload
        reference_layout = QtWidgets.QHBoxLayout()
        self.reference_upload_button = QtWidgets.QPushButton("Upload Reference AnsSheet (Optional)", self)
        self.reference_upload_button.setFont(button_font)
        self.reference_upload_button.setStyleSheet("background-color: #effdfe; color: #000000;")
        self.reference_upload_button.setFixedWidth(button_width)
        self.reference_upload_button.clicked.connect(self.upload_reference_pdf)
        reference_layout.addWidget(self.reference_upload_button)
        self.reference_status_label = QtWidgets.QLabel("No file selected", self)
        self.reference_status_label.setFont(label_font)
        self.reference_status_label.setStyleSheet("color: #000000;")
        reference_layout.addWidget(self.reference_status_label)
        layout.addLayout(reference_layout)

        # Add the Clear Button
        self.clear_button = QtWidgets.QPushButton("Clear All", self)
        self.clear_button.setFont(button_font)
        self.clear_button.setStyleSheet("background-color: #effdfe; color: #000000;")
        self.clear_button.clicked.connect(self.clear_selections)
        layout.addWidget(self.clear_button)

        # Start Checking Button
        self.start_checking_button = QtWidgets.QPushButton("Start Checking", self)
        self.start_checking_button.setFont(button_font)
        self.start_checking_button.setStyleSheet("background-color: #08292a; color: #FFFFFF;")
        self.start_checking_button.clicked.connect(self.start_checking)
        layout.addWidget(self.start_checking_button)

        # Set layout
        self.setLayout(layout)
        self.pdf_paths = {"Question Paper": "", "Reference Answer": "", "Actual Answer": ""}
        self.show()
        
    def update_frame(self):
        # Only advance frames when video is playing
        if self.video_playing:
            ret, frame = self.capture.read()
            if ret:
                # Convert the frame from BGR to RGB format
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(q_image))
            else:
                # Loop the video by resetting the frame position
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def closeEvent(self, event):
        # Release resources when closing
        self.capture.release()
        event.accept()
        
    def clear_selections(self):
        """Reset all file uploads and labels."""
        self.pdf_paths = {"Question Paper": "", "Reference Answer": "", "Actual Answer": ""}
        self.question_status_label.setText("No file selected")
        self.answer_status_label.setText("No file selected")
        self.reference_status_label.setText("No file selected")

        # Reset label colors
        self.question_status_label.setStyleSheet("color: #000000;")
        self.answer_status_label.setStyleSheet("color: #000000;")
        self.reference_status_label.setStyleSheet("color: #000000;")

    def upload_question_pdf(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Question Paper PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.pdf_paths["Question Paper"] = file_path
            self.question_status_label.setText("Uploaded")
            self.question_status_label.setStyleSheet("color: #28C76F;")
        else:
            self.question_status_label.setText("No file selected")

    def upload_answer_pdf(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Answer Sheet PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.pdf_paths["Actual Answer"] = file_path
            self.answer_status_label.setText("Uploaded")
            self.answer_status_label.setStyleSheet("color: #28C76F;")
        else:
            self.answer_status_label.setText("No file selected")

    def upload_reference_pdf(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Reference Answer Sheet PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.pdf_paths["Reference Answer"] = file_path
            self.reference_status_label.setText("Uploaded")
            self.reference_status_label.setStyleSheet("color: #28C76F;")
        else:
            self.reference_status_label.setText("No file selected")

    def start_checking(self):
        # Validate that the required files are uploaded
        if not self.pdf_paths["Question Paper"]:
            QtWidgets.QMessageBox.warning(self, "Missing Files", "Please upload a Question Paper PDF.")
            return
        if not self.pdf_paths["Actual Answer"]:
            QtWidgets.QMessageBox.warning(self, "Missing Files", "Please upload an Answer Sheet PDF.")
            return

        # Set up a progress dialog
        self.progress = QtWidgets.QProgressDialog("Processing PDFs...", "Cancel", 0, 100, self)
        self.progress.setWindowTitle("Please Wait")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)
        self.progress.show()
        self.progress.setValue(10)

        # Get the API key from environment variable, with a fallback default key
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDPuEDz-SY2gCRStIC1TOCf-GUyg477dZ0")
        
        # Construct the prompt for the Gemini API
        prompt = self.construct_prompt()
        
        # Start playing the video during processing
        self.video_playing = True
        
        # Create a worker thread for processing
        self.thread = QThread()
        self.worker = ProcessingWorker(api_key, self.pdf_paths, prompt)
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.processing_finished)
        
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.handle_result)
        self.worker.error.connect(self.handle_error)
        
        # Start the thread
        self.thread.start()
    
    def update_progress(self, value):
        """Update the progress dialog with the current progress value."""
        if hasattr(self, 'progress') and self.progress is not None:
            self.progress.setValue(value)
    
    def handle_result(self, response):
        """Handle the successful processing result."""
        # Generate a report with the response
        self.response_text = response
    
    def handle_error(self, error_message):
        """Handle errors during processing."""
        # Pause the video
        self.video_playing = False
        if hasattr(self, 'progress'):
            self.progress.close()
        QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred during processing: {error_message}")
        
    def processing_finished(self):
        """Handle the completion of the processing thread."""
        # Pause the video
        self.video_playing = False
        
        # Close the progress dialog
        if hasattr(self, 'progress'):
            self.progress.close()
            
        try:
            # Generate a report with the response
            report_path = self.generate_report(self.response_text)
            
            # Show completion message and open the report
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Checking Complete")
            msg_box.setText(f"Analysis complete! Report saved to:\n{report_path}")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
            button = msg_box.exec_()
            
            if button == QtWidgets.QMessageBox.Open:
                # Open the report file with the default application
                if sys.platform == 'win32':
                    os.startfile(report_path)
                elif sys.platform == 'darwin':  # macOS
                    os.system(f'open "{report_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{report_path}"')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred when generating the report: {str(e)}")
        
    def construct_prompt(self):
        """Construct the prompt for the Gemini API based on the uploaded files."""
        has_reference = bool(self.pdf_paths["Reference Answer"])
        return construct_prompt(has_reference)
    
    def generate_report(self, response_text):
        """Generate a Markdown report with the API response."""
        return generate_markdown_report(response_text)