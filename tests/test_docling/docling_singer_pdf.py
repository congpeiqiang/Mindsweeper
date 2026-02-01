from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline import Result
import json


def parse_pdf(pdf_path, output_dir='output'):
    """解析 PDF 并保存所有内容"""

    # 初始化转换器
    converter = DocumentConverter(
        extract_tables=True,
        extract_formulas=True,
        extract_pictures=True
    )

    # 转换 PDF
    result: Result = converter.convert(pdf_path)

    # 1. 保存 Markdown
    md_content = result.document.export_to_markdown()
    with open(f'{output_dir}/output.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

    # 2. 保存 JSON 结构化数据
    dict_data = result.document.export_to_dict()
    with open(f'{output_dir}/output.json', 'w', encoding='utf-8') as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=2)

    # 3. 提取所有表格到 CSV
    for i, table in enumerate(result.document.tables):
        table.df.to_csv(f'{output_dir}/table_{i}.csv', index=False)

    # 4. 保存所有图片
    for i, picture in enumerate(result.document.pictures):
        picture.save_image(f'{output_dir}/picture_{i}.png')

    return result


# 使用示例
result = parse_pdf('document.pdf')
print("解析完成！")