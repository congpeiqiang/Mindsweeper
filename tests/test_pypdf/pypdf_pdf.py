# _*_ coding:utf-8_*_
from io import BytesIO


def extract_pdf_pypdf(file_bytes: bytes, password: str = None) -> str:
    """Extract PDF content using pypdf (synchronous).

    Args:
        file_bytes: PDF file content as bytes
        password: Optional password for encrypted PDFs

    Returns:
        str: Extracted text content

    Raises:
        Exception: If PDF is encrypted and password is incorrect or missing
    """
    from pypdf import PdfReader  # type: ignore

    pdf_file = BytesIO(file_bytes)
    reader = PdfReader(pdf_file)

    # Check if PDF is encrypted
    if reader.is_encrypted:
        if not password:
            raise Exception("PDF is encrypted but no password provided")

        decrypt_result = reader.decrypt(password)
        if decrypt_result == 0:
            raise Exception("Incorrect PDF password")

    # Extract text from all pages
    content = ""
    for page in reader.pages:
        content += page.extract_text() + "\n"

    return content

path=r"E:\学习资料.pdf"
with open(path, "rb") as f:
    pdf_bytes = f.read()

content = extract_pdf_pypdf(pdf_bytes)
print("解析后的文档:")
print(content)