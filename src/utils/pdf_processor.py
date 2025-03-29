import os, base64, tempfile
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

class PDFProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def pdf_to_images(self, pdf_path):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()  
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(dpi=150)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                image_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
                image.save(image_path, "PNG")
                images.append(image_path)
        except Exception as e:
            print(f"Error processing PDF: {e}")
            # Cleanup on error
            self.cleanup_temp_dir(temp_dir)
            raise
        finally:
            pdf_document.close()
        return images, temp_dir

    def images_to_base64(self, image_paths, label):
        encoded_images = []
        for page_num, image_path in enumerate(image_paths):
            try:
                with open(image_path, "rb") as image_file:
                    img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    encoded_images.append({
                        "label": label,
                        "page_number": page_num + 1,
                        "img_base64": img_base64
                    })
            except Exception as e:
                print(f"Error encoding image {image_path}: {e}")
        return encoded_images

    def create_parts(self, text_prompt, encoded_images_sets):
        parts = [{"text": text_prompt}]
        for encoded_images in encoded_images_sets:
            for img in encoded_images:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img["img_base64"]
                    }
                })
        return parts

    def generate_response(self, parts):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(parts)
        return response.text

    def process_pdfs(self, pdf_paths, prompt_text):
        encoded_images_sets = []
        temp_dirs = []
        try:
            for label, pdf_path in pdf_paths.items():
                if pdf_path:
                    image_paths, temp_dir = self.pdf_to_images(pdf_path)
                    encoded_images = self.images_to_base64(image_paths, label)
                    encoded_images_sets.append(encoded_images)
                    temp_dirs.append(temp_dir)

            parts = self.create_parts(prompt_text, encoded_images_sets)
            response_text = self.generate_response(parts)
            return response_text
        finally:
            # Cleanup: remove the temporary directories
            for temp_dir in temp_dirs:
                self.cleanup_temp_dir(temp_dir)

    def cleanup_temp_dir(self, temp_dir):
        try:
            for image_path in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, image_path))
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp directory {temp_dir}: {e}")