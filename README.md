# Rison-Copy-Checker

## Project Description

**Rison-Copy-Checker** is a Python-based application designed to automatically evaluate university exam answer sheets. The application uses a GUI where users can upload a PDF of the question paper, the answer sheet, and optionally a reference marking scheme. The project uses the Gemini API (Flash 1.5 model) to analyze the answer sheet and provide a detailed report with correctness, marks, and analysis for each question.

## Installation Instructions

### Prerequisites

Before you begin, ensure you have Python 3.x installed on your machine. Additionally, you will need to install the required dependencies.

### Step 1: Clone the repository

Clone this repository to your local machine using the following command:

```
git clone https://github.com/rishb0/Rison-Copy-Checker.git
```

### Step 2: Install dependencies

Navigate to the project folder and install the required Python modules using the `install-dependencies.bat` script:

1. **Run `install-dependencies.bat`** by double-clicking it or running it from the command prompt. This will automatically install the necessary modules listed in `requirements.txt`.
   
Alternatively, you can manually install the dependencies by running the following command:

```
pip install -r requirements.txt
```
or
```
pip install PyQt5>=5.15.4 PyQtWebEngine>=5.15.4 PyMuPDF>=1.19.5 Pillow>=9.0.0 google-generativeai>=0.3.0 opencv-python>=4.5.5 markdown>=3.3.6 python-docx>=0.8.11 python-pptx>=0.6.20 cairosvg>=2.5.2 numpy>=1.22.0 reportlab>=3.6.6
```
### Step 3: API Key

To use the Gemini API, you need an API key. Enter the API key when you firstime run the `RisonCopyChecker.py` 

To get the API-KEY visit : https://aistudio.google.com/apikey

## Usage

1. Ensure your machine is connected to the internet.
2. Open the `RisonCopyChecker.py` file in your terminal or Visual Studio Code.
3. Run the project by executing the following command:

```
python RisonCopyChecker.py
```

4. The GUI will open. Upload the **question paper PDF**, **answer sheet PDF**, and optionally a **reference marking scheme**.
5. Click on **Start Checking**. The program will analyze the answer sheet and generate a report with correctness, marks, and detailed analysis for each question.
6. The time taken for the analysis will depend on the size of the PDF files and the speed of your internet connection.


## Contact

For any inquiries or issues, please feel free to reach out via GitHub: [@rishb0](https://github.com/rishb0).

## Screenshots

![GUI Look](GUI-screenshot.png)
