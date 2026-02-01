from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionResult
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from pathlib import Path


def advanced_pdf_parsing(pdf_path: str, output_dir: str = "output"):
    """
    高级PDF解析示例，提取所有内容
    """
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)

    # 1. 配置转换器（启用所有提取功能）
    converter = DocumentConverter(
        # 格式选项配置
        format_options={
            "pdf": {
                "backend": PyPdfiumDocumentBackend,
                "pipeline_options": {
                    "extract_tables": True,
                    "extract_formulas": True,
                    "extract_pictures": True,
                    "extract_paragraphs": True,
                    "extract_headings": True,
                    "extract_lists": True,
                    "ocr_enabled": True,  # 启用OCR
                    "ocr_languages": ["en", "zh"]  # 支持中英文
                }
            }
        }
    )

    # 2. 执行转换
    print(f"正在解析: {pdf_path}")
    result: ConversionResult = converter.convert(pdf_path)

    if result.status.name not in ["SUCCESS", "PARTIAL_SUCCESS"]:
        print("解析失败")
        return

    document = result.document

    # 3. 提取和保存各种内容
    print("\n=== 提取结果 ===")

    # 3.1 保存完整Markdown文档
    md_output = Path(output_dir) / f"{Path(pdf_path).stem}.md"
    with open(md_output, "w", encoding="utf-8") as f:
        f.write(document.export_to_markdown())
    print(f"✓ Markdown文档已保存: {md_output}")

    # 3.2 提取和保存表格
    tables = document.tables
    print(f"✓ 发现 {len(tables)} 个表格")

    for i, table in enumerate(tables):
        # 保存为CSV
        csv_path = Path(output_dir) / f"table_{i + 1}.csv"
        table.df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        # 保存为Excel
        excel_path = Path(output_dir) / f"table_{i + 1}.xlsx"
        table.df.to_excel(excel_path, index=False)

        print(f"  表格{i + 1}: {table.caption or '无标题'}")
        print(f"    位置: 第{table.location.page}页")
        print(f"    形状: {table.df.shape}")

    # 3.3 提取和保存图片
    pictures = document.pictures
    print(f"✓ 发现 {len(pictures)} 张图片")

    for i, picture in enumerate(pictures):
        img_path = Path(output_dir) / f"picture_{i + 1}.png"
        picture.save_image(img_path)

        print(f"  图片{i + 1}: {picture.caption or '无描述'}")
        print(f"    格式: {picture.format}")

    # 3.4 提取公式
    formulas = document.formulas
    print(f"✓ 发现 {len(formulas)} 个公式")

    if formulas:
        formulas_path = Path(output_dir) / "formulas.txt"
        with open(formulas_path, "w", encoding="utf-8") as f:
            for i, formula in enumerate(formulas):
                f.write(f"公式 {i + 1}:\n")
                f.write(f"LaTeX: {formula.latex}\n")
                f.write(f"位置: 第{formula.location.page}页\n")
                f.write("-" * 50 + "\n")

    # 3.5 生成处理报告
    generate_parsing_report(document, output_dir)

    return document


def generate_parsing_report(document, output_dir):
    """生成解析报告"""
    report = {
        "统计信息": {
            "总页数": len(document.pages),
            "表格数量": len(document.tables),
            "图片数量": len(document.pictures),
            "公式数量": len(document.formulas),
            "段落数量": sum(len(page.paragraphs) for page in document.pages if hasattr(page, 'paragraphs')),
            "标题数量": sum(len(page.headings) for page in document.pages if hasattr(page, 'headings')),
        },
        "页面详情": [
            {
                "页码": page.number,
                "文本长度": len(page.text) if hasattr(page, 'text') else 0,
                "元素数量": len(page.elements) if hasattr(page, 'elements') else 0,
            }
            for page in document.pages
        ]
    }

    import json
    report_path = Path(output_dir) / "parsing_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✓ 解析报告已保存: {report_path}")


# 使用示例
advanced_pdf_parsing("sample.pdf", "parsed_output")