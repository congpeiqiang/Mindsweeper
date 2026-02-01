from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionResult

def basic_pdf_parsing(pdf_path: str):
    """
    基础PDF解析示例
    """
    # 1. 创建转换器实例
    converter = DocumentConverter()

    # 2. 转换PDF文件
    result: ConversionResult = converter.convert(pdf_path)

    # 3. 检查转换状态
    print(f"转换状态: {result.status}")
    print(f"输入文件: {result.input.file.name}")
    print(f"文档格式: {result.input.format}")

    # 4. 获取文档对象（转换成功时）
    if result.status.name in ["SUCCESS", "PARTIAL_SUCCESS"]:
        document = result.document

        # 5. 导出为不同格式
        # 5.1 Markdown格式
        markdown_content = document.export_to_markdown()
        print("\n=== Markdown 格式 ===")
        print(markdown_content[:500] + "...")  # 显示前500字符

        # 5.2 JSON格式
        json_data = document.export_to_dict()
        print(f"\n=== JSON 数据结构 ===")
        print(f"文档总页数: {len(json_data.get('pages', []))}")

        # 5.3 纯文本格式
        plain_text = document.export_to_text()
        print(f"\n=== 纯文本长度 ===")
        print(f"字符数: {len(plain_text)}")

    else:
        print("转换失败:")
        for error in result.errors:
            print(f"- {error.error_message}")


# 使用示例
basic_pdf_parsing("sample.pdf")