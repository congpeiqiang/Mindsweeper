# PDF 处理器
"""
PDF 文档处理器，支持文本提取和缓存
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# pip install -qU langchain-pymupdf4llm

import tempfile
import os
import logging
import hashlib
import time
from typing import Optional

# 尝试导入 PDF 处理库
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    PyPDFLoader = None

try:
    from langchain_pymupdf4llm import PyMuPDF4LLMLoader
except ImportError:
    PyMuPDF4LLMLoader = None

logger = logging.getLogger(__name__)

# PDF 内容缓存，避免重复解析同一个文件
_pdf_cache = {}


def _safe_delete_temp_file(file_path: str, max_retries: int = 3, delay: float = 0.1):
    """
    安全删除临时文件，处理Windows文件锁定问题

    Args:
        file_path: 要删除的文件路径
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    """
    if not os.path.exists(file_path):
        return

    for attempt in range(max_retries):
        try:
            os.unlink(file_path)
            logger.debug(f"临时文件已删除: {file_path}")
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                logger.debug(f"删除临时文件失败（尝试 {attempt + 1}/{max_retries}），等待后重试: {e}")
                time.sleep(delay)
            else:
                logger.warning(f"无法删除临时文件（已重试{max_retries}次），文件将由系统清理: {file_path}")
        except Exception as e:
            logger.warning(f"删除临时文件时发生异常: {e}")
            break


class PDFProcessor:
    """PDF 处理器类"""
    @classmethod
    def extract_text(cls, temp_file_path: str, filename: str = "unknown.pdf") -> str:
        """从PDF字节数据中提取文本"""
        return cls.extract_pdf_text(temp_file_path, filename)

    @classmethod
    def extract_pdf_text(cls, temp_file_path: str, filename: str = "unknown.pdf", cache: Optional[dict] = None) -> str:
        """
        从PDF字节数据中提取文本，使用缓存避免重复解析
        提取的方法：
        1、langchain pdf加载器：https://docs.langchain.com/oss/python/integrations/document_loaders/index#pdfs
            推荐 pip install -qU langchain-community langchain-pymupdf4llm，支持基于多模态大模型进行图片解析
        2、DeepSeek ocr大模型
        3、PaddleOCR VL 0.9B（推荐）--部署需要GPU
            推荐 https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PaddleOCR-VL.html

        """
        try:
            if not os.path.exists(temp_file_path):
                logger.error(f"PDF文件不存在: {temp_file_path}")
                return f"PDF文件不存在: {temp_file_path}"
            # 优先使用 PyMuPDF4LLM
            if PyMuPDF4LLMLoader is not None:
                try:
                    logger.info(f"使用 PyMuPDF4LLM 解析PDF: {filename}")
                    loader = PyMuPDF4LLMLoader(
                        temp_file_path,
                        mode="single",  # 作为单个文档处理
                        extract_images=False,  # 提取图片
                        table_strategy="lines"  # 提取表格
                    )
                    documents = loader.load()
                    if documents:
                        text_content = documents[0].page_content
                        logger.info(f"PyMuPDF4LLM 解析成功，内容长度: {len(text_content)} 字符")
                    else:
                        text_content = "PDF文件解析后内容为空"

                except Exception as e:
                    logger.warning(f"PyMuPDF4LLM 解析失败，尝试备用方法: {e}")
                    text_content = f"PDF文件处理出错: {str(e)}"

                # 如果仍然没有内容
                if not text_content:
                    text_content = "PDF文件无法解析或内容为空"

                return text_content
            else:
                return f"PDF文件处理出错: PyMuPDF4LLMLoadere未安装!"
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            return f"PDF文件处理出错: {str(e)}"

