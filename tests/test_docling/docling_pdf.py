# _*_ coding:utf-8_*_
from pathlib import Path


def convert_with_docling(file_path: Path) -> str:
    """Convert document using docling (synchronous).

    Args:
        file_path: Path to the document file

    Returns:
        str: Extracted markdown content
    """
    from docling.document_converter import DocumentConverter  # type: ignore

    converter = DocumentConverter()
    result = converter.convert(file_path)
    return result.document.export_to_markdown()

path=r"E:\学习资料.pdf"
convert_with_docling(Path(path))