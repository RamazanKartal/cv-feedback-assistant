"""
Document Parser Service
Extracts text from PDF and DOCX files
"""

import io
from typing import Optional, Tuple


class DocumentParser:
    """Extract text from PDF and DOCX files"""

    SUPPORTED_TYPES = {
        'pdf': ['application/pdf'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    }

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from PDF using multiple methods for reliability

        Args:
            file_bytes: PDF file as bytes

        Returns:
            Extracted text content
        """
        text = ""

        # Try pdfplumber first (better for complex layouts)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            pass

        # Fallback to PyPDF2 if pdfplumber fails or returns empty
        if not text.strip():
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception:
                pass

        return text.strip()

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """
        Extract text from DOCX file

        Args:
            file_bytes: DOCX file as bytes

        Returns:
            Extracted text content
        """
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))

            # Extract text from paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        paragraphs.append(" | ".join(row_text))

            return "\n".join(paragraphs).strip()
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    @classmethod
    def parse_file(cls, uploaded_file) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse uploaded file based on its type

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name.lower()

            if file_name.endswith('.pdf'):
                text = cls.extract_from_pdf(file_bytes)
                if not text:
                    return None, "Could not extract text from PDF. The file may be scanned or image-based."
                return text, None

            elif file_name.endswith('.docx'):
                text = cls.extract_from_docx(file_bytes)
                if not text:
                    return None, "Could not extract text from DOCX. The file may be empty."
                return text, None

            elif file_name.endswith('.doc'):
                return None, "Old .doc format is not supported. Please convert to .docx"

            else:
                return None, f"Unsupported file type. Please upload PDF or DOCX files."

        except Exception as e:
            return None, f"Error parsing file: {str(e)}"

    @staticmethod
    def get_file_info(uploaded_file) -> dict:
        """
        Get information about uploaded file

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            Dict with file information
        """
        return {
            "name": uploaded_file.name,
            "size": uploaded_file.size,
            "type": uploaded_file.type,
            "size_kb": round(uploaded_file.size / 1024, 2)
        }
