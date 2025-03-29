import os
import sys
import cv2
import markdown
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets

# Add the current directory to the path so imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the main application class
from src.ui.main_window import RisonCopyChecker
from src.ui.report_generator import generate_markdown_report
from src.ui.api_key_dialog import ApiKeyDialog
from src.utils.api_key_manager import ApiKeyManager

class MarkdownReportViewer(QtWidgets.QWidget):
    """A window for displaying Markdown reports"""
    def __init__(self, report_path):
        super().__init__()
        self.report_path = report_path
        self.setWindowTitle("Rison Copy Checker - Report Viewer")
        self.setup_ui()
        self.load_report()
        
    def setup_ui(self):
        # Set up a resizable window that's 80% of screen size
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window_width = int(screen.width() * 0.8)
        window_height = int(screen.height() * 0.8)
        x = int((screen.width() - window_width) / 2)
        y = int((screen.height() - window_height) / 2)
        self.setGeometry(x, y, window_width, window_height)
        
        # Set icon
        icon_path = os.path.join(current_dir, "attached_assets", "rison icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Create web view for rendering HTML
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Add a close button
        close_button = QtWidgets.QPushButton("Close Report")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("background-color: #052123; color: #FFFFFF; padding: 10px;")
        close_button.setFont(QtGui.QFont("Arial", 12))
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def load_report(self):
        """Load and convert the Markdown file to HTML for display"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert Markdown to HTML
            html_content = markdown.markdown(md_content, extensions=['tables'])
            
            # Add CSS for styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                        background-color: #fff;
                    }}
                    h1 {{
                        color: #052123;
                        padding-bottom: 10px;
                        border-bottom: 2px solid #97F4FC;
                    }}
                    h2 {{
                        color: #052123;
                        margin-top: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        padding: 12px 15px;
                        border: 1px solid #ddd;
                        text-align: left;
                    }}
                    th {{
                        background-color: #052123;
                        color: #fff;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                    code {{
                        background-color: #f5f5f5;
                        padding: 2px 5px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f5f5f5;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Load the HTML content into the web view
            self.web_view.setHtml(styled_html, QtCore.QUrl("file://"))
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load report: {str(e)}")


class EnhancedRisonCopyChecker(RisonCopyChecker):
    """Enhanced version of RisonCopyChecker with improved UI and report viewing"""
    def __init__(self):
        super().__init__()
        
        # Make window maximized
        self.showMaximized()
        
        # Update path references for icons and videos
        self.update_asset_paths()
        
        # Override the generate_report method to use our custom report viewer
        self.original_generate_report = self.generate_report
        self.generate_report = self.enhanced_generate_report
        
        # Add a status panel on the right side
        self.setup_status_panel()
        
        # Center all buttons
        self.center_ui_elements()
        
        # Add a menu bar with API key management
        self.setup_menu_bar()
        
        # Check for API key on startup
        self.check_api_key()
        
    def setup_menu_bar(self):
        """Create a menu bar with settings options"""
        # Create menu bar
        menu_bar = QtWidgets.QMenuBar(self)
        self.layout().setMenuBar(menu_bar)
        
        # Create Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        
        # Add API Key action
        api_key_action = QtWidgets.QAction("Manage API Key", self)
        api_key_action.triggered.connect(self.show_api_key_dialog)
        settings_menu.addAction(api_key_action)
        
    def show_api_key_dialog(self):
        """Show the API key dialog to update the API key"""
        current_key = ApiKeyManager.get_api_key()
        dialog = ApiKeyDialog(self, current_key)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Get the API key from the dialog
            api_key = dialog.get_api_key()
            if api_key:
                # Save the API key
                ApiKeyManager.save_api_key(api_key, dialog.should_save_key())
                if hasattr(self, 'status_box'):
                    self.status_box.setText("API Key Updated")
                    self.status_box.setStyleSheet("background-color: #002021; color: #28C76F; padding: 20px; border-radius: 0px;")
                QtWidgets.QMessageBox.information(self, "API Key Updated", "Your API key has been updated successfully!")
        
    def check_api_key(self):
        """Check if API key exists and prompt user if not"""
        api_key = ApiKeyManager.get_api_key()
        if not api_key:
            if hasattr(self, 'status_box'):
                self.status_box.setText("API Key Required")
                self.status_box.setStyleSheet("background-color: #002021; color: #FF9500; padding: 20px; border-radius: 0px;")
            
            # Show welcome message with API key information
            QtWidgets.QMessageBox.information(
                self, 
                "Welcome to Rison Copy Checker", 
                "Welcome to Rison Copy Checker!\n\n"
                "This application uses Google's Gemini API to analyze exam papers.\n"
                "You'll need to provide your own API key from Google AI Studio.\n\n"
                "Click OK to enter your API key."
            )
            
            # Show the API key dialog
            dialog = ApiKeyDialog(self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                # Get the API key from the dialog
                api_key = dialog.get_api_key()
                if api_key:
                    # Save the API key
                    ApiKeyManager.save_api_key(api_key, dialog.should_save_key())
                    if hasattr(self, 'status_box'):
                        self.status_box.setText("API Key Saved")
                        self.status_box.setStyleSheet("background-color: #002021; color: #28C76F; padding: 20px; border-radius: 0px;")
                else:
                    if hasattr(self, 'status_box'):
                        self.status_box.setText("No API Key Provided")
                        self.status_box.setStyleSheet("background-color: #002021; color: #FF9500; padding: 20px; border-radius: 0px;")
            else:
                if hasattr(self, 'status_box'):
                    self.status_box.setText("No API Key Provided")
                    self.status_box.setStyleSheet("background-color: #002021; color: #FF9500; padding: 20px; border-radius: 0px;")
        
    def clear_selections(self):
        """Override clear_selections to reset the status panel as well"""
        # Call the parent method to clear selections
        super().clear_selections()
        
        # Reset status panel
        if hasattr(self, 'status_box'):
            self.status_box.setText("Idle")
            self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
            self.status_progress.setValue(0)
            self.status_progress.setVisible(False)
            
    def upload_question_pdf(self):
        """Override upload_question_pdf to update status panel"""
        # Call the parent method
        super().upload_question_pdf()
        
        # Update status panel
        if hasattr(self, 'status_box') and self.pdf_paths["Question Paper"]:
            self.status_box.setText(f"Question Paper uploaded:\n{os.path.basename(self.pdf_paths['Question Paper'])}")
            self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
            
    def upload_answer_pdf(self):
        """Override upload_answer_pdf to update status panel"""
        # Call the parent method
        super().upload_answer_pdf()
        
        # Update status panel
        if hasattr(self, 'status_box') and self.pdf_paths["Actual Answer"]:
            self.status_box.setText(f"Answer Sheet uploaded:\n{os.path.basename(self.pdf_paths['Actual Answer'])}")
            self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
            
    def upload_reference_pdf(self):
        """Override upload_reference_pdf to update status panel"""
        # Call the parent method
        super().upload_reference_pdf()
        
        # Update status panel
        if hasattr(self, 'status_box') and self.pdf_paths["Reference Answer"]:
            self.status_box.setText(f"Reference Answer uploaded:\n{os.path.basename(self.pdf_paths['Reference Answer'])}")
            self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
        
    def center_ui_elements(self):
        """Center all buttons and UI elements"""
        # Find all buttons and layouts in the main layout
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            # If item is a horizontal layout with buttons, center it
            if isinstance(item, QtWidgets.QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QtWidgets.QPushButton):
                        # Center this horizontal layout
                        item.setAlignment(QtCore.Qt.AlignCenter)
                        # Center widgets inside
                        for k in range(item.count()):
                            item.setAlignment(item.itemAt(k).widget(), QtCore.Qt.AlignCenter)
            # If item is directly a button, center it
            elif isinstance(item.widget(), QtWidgets.QPushButton):
                self.layout().setAlignment(item.widget(), QtCore.Qt.AlignCenter)
                
    def start_checking(self):
        """Override start_checking to update the status panel"""
        # First check if we can upload the files
        if not self.pdf_paths["Question Paper"]:
            QtWidgets.QMessageBox.warning(self, "Missing Files", "Please upload a Question Paper PDF.")
            if hasattr(self, 'status_box'):
                self.status_box.setText("Missing Question Paper")
                self.status_box.setStyleSheet("background-color: #002021; color: #FF0000; padding: 20px; border-radius: 0px;")
            return
            
        if not self.pdf_paths["Actual Answer"]:
            QtWidgets.QMessageBox.warning(self, "Missing Files", "Please upload an Answer Sheet PDF.")
            if hasattr(self, 'status_box'):
                self.status_box.setText("Missing Answer Sheet")
                self.status_box.setStyleSheet("background-color: #002021; color: #FF0000; padding: 20px; border-radius: 0px;")
            return
        
        # Check for API key and prompt if not available
        api_key = ApiKeyManager.get_api_key()
        if not api_key:
            if hasattr(self, 'status_box'):
                self.status_box.setText("API Key Required")
                self.status_box.setStyleSheet("background-color: #002021; color: #FF9500; padding: 20px; border-radius: 0px;")
            
            # Show the API key dialog
            dialog = ApiKeyDialog(self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                # Get the API key from the dialog
                api_key = dialog.get_api_key()
                if api_key:
                    # Save the API key
                    ApiKeyManager.save_api_key(api_key, dialog.should_save_key())
                else:
                    QtWidgets.QMessageBox.warning(self, "Missing API Key", "An API key is required to use this application.")
                    return
            else:
                # User cancelled the dialog
                return
        
        # Update our status panel
        if hasattr(self, 'status_box'):
            self.status_box.setText("Processing PDFs... 10%")
            self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
            self.status_progress.setValue(10)
            self.status_progress.setVisible(True)
            
        # Call the parent class's start_checking method to do the actual work
        super().start_checking()
    
    def setup_status_panel(self):
        """Create a status panel on the right side of the window"""
        # Create a horizontal layout to hold the main content and status panel
        main_horizontal_layout = QtWidgets.QHBoxLayout()
        
        # Get the current layout
        current_layout = self.layout()
        
        # Take all items from the current layout
        items = []
        for i in range(current_layout.count()):
            items.append(current_layout.itemAt(0))
            current_layout.removeItem(current_layout.itemAt(0))
        
        # Create a new vertical layout for the main content
        main_content_layout = QtWidgets.QVBoxLayout()
        
        # Add all items back to the main content layout
        for item in items:
            if item is not None:
                if item.widget():
                    main_content_layout.addWidget(item.widget())
                elif item.layout():
                    main_content_layout.addLayout(item.layout())
        
        # Add the main content layout to the horizontal layout
        main_horizontal_layout.addLayout(main_content_layout, 7)  # 70% width
        
        # Create the status panel
        self.status_panel = QtWidgets.QWidget()
        status_layout = QtWidgets.QVBoxLayout(self.status_panel)
        
        # Add status title
        status_title = QtWidgets.QLabel("Status")
        status_title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        status_title.setAlignment(QtCore.Qt.AlignCenter)
        status_title.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 10px;")
        status_layout.addWidget(status_title)
        
        # Add some spacing between title and status box
        status_layout.addSpacing(10)
        
        # Add status content box
        self.status_box = QtWidgets.QLabel("Idle")
        self.status_box.setFont(QtGui.QFont("Arial", 14))
        self.status_box.setAlignment(QtCore.Qt.AlignCenter)
        self.status_box.setStyleSheet("background-color: #002021; color: #FFFFFF; padding: 20px; border-radius: 0px;")
        self.status_box.setMinimumHeight(180)  # Make it taller to match reference
        status_layout.addWidget(self.status_box)
        
        # Add progress bar
        self.status_progress = QtWidgets.QProgressBar()
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        self.status_progress.setVisible(False)
        status_layout.addWidget(self.status_progress)
        
        # Add spacer to push content to the top
        status_layout.addStretch()
        
        # Add the status panel to the horizontal layout
        main_horizontal_layout.addWidget(self.status_panel, 3)  # 30% width
        
        # Set the new layout to the widget
        current_layout.addLayout(main_horizontal_layout)

    def update_asset_paths(self):
        """Update asset paths to use absolute paths in the cloned repository structure"""
        # Update video path
        video_path = os.path.join(current_dir, "attached_assets", "HDRobotVideo.mp4")
        if os.path.exists(video_path) and hasattr(self, 'capture'):
            self.capture.release()  # Release the current capture
            self.capture = cv2.VideoCapture(video_path)
        
        # Update icon path
        icon_path = os.path.join(current_dir, "attached_assets", "rison icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
    
    def enhanced_generate_report(self, response_text):
        """Generate a report with support for our custom viewer"""
        # Call the original method to generate the report file
        report_path = self.original_generate_report(response_text)
        
        # Return the path to the report
        return report_path
        
    def update_progress(self, value):
        """Override update_progress to use our status panel instead of progress dialog"""
        # Update the original progress dialog if it exists
        if hasattr(self, 'progress') and self.progress is not None:
            self.progress.setValue(value)
            
        # Update our status panel if it exists
        if hasattr(self, 'status_progress'):
            self.status_progress.setValue(value)
            self.status_box.setText(f"Processing PDFs... {value}%")
            
    def handle_result(self, response):
        """Override handle_result to update our status panel"""
        # Call the original method to store the response
        self.response_text = response
        
        # Update status panel
        if hasattr(self, 'status_box'):
            self.status_box.setText("Analysis complete!")
            self.status_box.setStyleSheet("background-color: #002021; color: #28C76F; padding: 20px; border-radius: 0px;")
            
    def handle_error(self, error_message):
        """Override handle_error to update our status panel"""
        # Pause the video
        self.video_playing = False
        
        # Update status panel
        if hasattr(self, 'status_box'):
            self.status_box.setText(f"Error: {error_message}")
            self.status_box.setStyleSheet("background-color: #002021; color: #FF0000; padding: 20px; border-radius: 0px;")
            self.status_progress.setVisible(False)
        
        # Close the progress dialog if it exists
        if hasattr(self, 'progress'):
            self.progress.close()
            
        # Show error message
        QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred during processing: {error_message}")
            
    def processing_finished(self):
        """Override processing_finished to use our custom report viewer and status panel"""
        # Pause the video
        self.video_playing = False
        
        # Update status panel
        if hasattr(self, 'status_progress'):
            self.status_progress.setVisible(False)
        
        # Close the progress dialog if it exists
        if hasattr(self, 'progress'):
            self.progress.close()
            
        try:
            # Generate a report with the response
            report_path = self.generate_report(self.response_text)
            
            # Update status panel with success message
            if hasattr(self, 'status_box'):
                self.status_box.setText(f"Report saved to:\n{os.path.basename(report_path)}")
                self.status_box.setStyleSheet("background-color: #002021; color: #28C76F; padding: 20px; border-radius: 0px;")
            
            # Show completion message with option to view report
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Checking Complete")
            msg_box.setText(f"Analysis complete! Report saved to:\n{report_path}")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
            button = msg_box.exec_()
            
            if button == QtWidgets.QMessageBox.Open:
                # Show our custom report viewer instead of using external app
                self.report_viewer = MarkdownReportViewer(report_path)
                self.report_viewer.show()
                
        except Exception as e:
            # Update status panel with error message
            if hasattr(self, 'status_box'):
                self.status_box.setText(f"Error generating report: {str(e)}")
                self.status_box.setStyleSheet("background-color: #002021; color: #FF0000; padding: 20px; border-radius: 0px;")
                
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred when generating the report: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EnhancedRisonCopyChecker()
    sys.exit(app.exec_())