from PyQt5 import QtWidgets, QtCore, QtGui

class ApiKeyDialog(QtWidgets.QDialog):
    """Dialog for entering or updating the Google Gemini API key"""
    
    def __init__(self, parent=None, current_key=""):
        super().__init__(parent)
        self.setWindowTitle("Google Gemini API Key")
        self.resize(500, 200)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label
        info_label = QtWidgets.QLabel(
            "To use Rison Copy Checker, you need a Google Gemini API key.\n"
            "Visit https://aistudio.google.com/apikey to get your API key."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Link label with clickable URL
        link_label = QtWidgets.QLabel(
            "<a href='https://aistudio.google.com/apikey'>Click here to get your API key</a>"
        )
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(link_label)
        
        # API Key input
        form_layout = QtWidgets.QFormLayout()
        self.api_key_input = QtWidgets.QLineEdit(current_key)
        self.api_key_input.setMinimumWidth(350)
        self.api_key_input.setPlaceholderText("Enter your Gemini API key here")
        form_layout.addRow("API Key:", self.api_key_input)
        layout.addLayout(form_layout)
        
        # Save to environment checkbox
        self.save_checkbox = QtWidgets.QCheckBox("Remember this API key for future sessions")
        self.save_checkbox.setChecked(True)
        layout.addWidget(self.save_checkbox)
        
        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_api_key(self):
        """Return the entered API key"""
        return self.api_key_input.text().strip()
    
    def should_save_key(self):
        """Return whether the key should be saved"""
        return self.save_checkbox.isChecked()