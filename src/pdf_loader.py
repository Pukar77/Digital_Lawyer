import fitz  # PyMuPDF
import re

class PDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_and_clean(self):
        """Reads PDF and returns a single cleaned string."""
        print(f"📄 Loading {self.file_path}...")
        try:
            doc = fitz.open(self.file_path)
        except Exception as e:
            print(f"❌ Error opening file: {e}")
            return ""

        full_text = ""
        for page in doc:
            text = page.get_text()
            # Clean page numbers and headers
            text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
            text = text.replace("Constitution of Nepal", "")
            full_text += text

        # Normalize whitespace
        cleaned_text = re.sub(r'\s+', ' ', full_text).strip()
        print(f"✅ PDF converted to text ({len(cleaned_text)} chars).")
        return cleaned_text