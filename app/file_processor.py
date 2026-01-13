from pathlib import Path
import pypdf
from docx import Document


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files

    Args:
        file_path: Path to the file

    Returns:
        Extracted text content

    Raises:
        ValueError: If file type is not supported
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == '.pdf':
        return extract_from_pdf(path)
    elif suffix in ['.docx', '.doc']:
        return extract_from_docx(path)
    elif suffix == '.txt':
        return extract_from_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .pdf, .docx, .txt")


def extract_from_pdf(path: Path) -> str:
    """Extract text from PDF file"""
    text_parts = []

    try:
        with open(path, 'rb') as file:
            reader = pypdf.PdfReader(file)

            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"[Page {page_num}]\n{page_text}")

        return '\n\n'.join(text_parts)

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def extract_from_docx(path: Path) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(path)
        paragraphs = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        return '\n'.join(paragraphs)

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX: {e}")


def extract_from_txt(path: Path) -> str:
    """Extract text from TXT file"""
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        return path.read_text(encoding='latin-1')
    except Exception as e:
        raise RuntimeError(f"Failed to read text file: {e}")
