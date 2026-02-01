from docling.document_converter import DocumentConverter
from pathlib import Path
import concurrent.futures
import json
from typing import List, Dict


class BatchPDFProcessor:
    """批量PDF处理器"""

    def __init__(self, output_base_dir: str = "batch_output"):
        self.converter = DocumentConverter(
            format_options={
                "pdf": {
                    "pipeline_options": {
                        "extract_tables": True,
                        "extract_pictures": True
                    }
                }
            }
        )
        self.output_base = Path(output_base_dir)
        self.output_base.mkdir(exist_ok=True)

    def process_single_pdf(self, pdf_path: Path) -> Dict:
        """处理单个PDF"""
        try:
            print(f"处理: {pdf_path.name}")

            # 创建文档输出目录
            doc_output = self.output_base / pdf_path.stem
            doc_output.mkdir(exist_ok=True)

            # 转换文档
            result = self.converter.convert(
                str(pdf_path),
                raises_on_error=False  # 不抛出异常，继续处理其他文件
            )

            if result.status.name not in ["SUCCESS", "PARTIAL_SUCCESS"]:
                return {
                    "file": pdf_path.name,
                    "status": result.status.name,
                    "errors": [e.error_message for e in result.errors],
                    "success": False
                }

            document = result.document

            # 保存文档内容
            self._save_document_content(document, doc_output)

            return {
                "file": pdf_path.name,
                "status": result.status.name,
                "pages": len(document.pages),
                "tables": len(document.tables),
                "pictures": len(document.pictures),
                "output_dir": str(doc_output),
                "success": True
            }

        except Exception as e:
            return {
                "file": pdf_path.name,
                "status": "ERROR",
                "errors": [str(e)],
                "success": False
            }

    def _save_document_content(self, document, output_dir: Path):
        """保存文档内容"""
        # 保存Markdown
        md_path = output_dir / "document.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(document.export_to_markdown())

        # 保存JSON
        json_path = output_dir / "document.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(document.export_to_dict(), f, indent=2, ensure_ascii=False)

        # 保存表格
        tables_dir = output_dir / "tables"
        tables_dir.mkdir(exist_ok=True)
        for i, table in enumerate(document.tables):
            csv_path = tables_dir / f"table_{i + 1}.csv"
            table.df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    def process_batch(self, pdf_files: List[str], max_workers: int = 4) -> List[Dict]:
        """批量处理PDF文件"""
        pdf_paths = [Path(f) for f in pdf_files]

        print(f"开始批量处理 {len(pdf_paths)} 个PDF文件...")
        print(f"使用 {max_workers} 个并行工作线程")

        results = []

        # 使用线程池并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pdf = {
                executor.submit(self.process_single_pdf, pdf_path): pdf_path
                for pdf_path in pdf_paths
            }

            for future in concurrent.futures.as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)

                    if result["success"]:
                        print(f"✓ 完成: {pdf_path.name}")
                    else:
                        print(f"✗ 失败: {pdf_path.name} - {result['status']}")

                except Exception as e:
                    error_result = {
                        "file": pdf_path.name,
                        "status": "EXCEPTION",
                        "errors": [str(e)],
                        "success": False
                    }
                    results.append(error_result)
                    print(f"✗ 异常: {pdf_path.name} - {str(e)}")

        # 生成批量处理报告
        self._generate_batch_report(results)

        return results

    def _generate_batch_report(self, results: List[Dict]):
        """生成批量处理报告"""
        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful

        report = {
            "处理摘要": {
                "总文件数": total,
                "成功数": successful,
                "失败数": failed,
                "成功率": f"{(successful / total * 100):.1f}%" if total > 0 else "0%"
            },
            "详细结果": results,
            "成功文件统计": {
                "总页数": sum(r.get("pages", 0) for r in results if r["success"]),
                "总表格数": sum(r.get("tables", 0) for r in results if r["success"]),
                "总图片数": sum(r.get("pictures", 0) for r in results if r["success"]),
            }
        }

        report_path = self.output_base / "batch_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' * 50}")
        print(f"批量处理完成!")
        print(f"总文件: {total}, 成功: {successful}, 失败: {failed}")
        print(f"详细报告: {report_path}")
        print(f"{'=' * 50}")


# 使用示例
if __name__ == "__main__":
    # 准备PDF文件列表
    import glob

    pdf_files = glob.glob("pdf_documents/*.pdf")

    if not pdf_files:
        print("未找到PDF文件")
    else:
        # 创建处理器
        processor = BatchPDFProcessor("batch_processing_results")

        # 执行批量处理
        results = processor.process_batch(pdf_files, max_workers=2)