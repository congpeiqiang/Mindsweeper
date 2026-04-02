# 类概述
PyMuPDF4LLMLoader 是一个 PDF 文档加载器，使用 PyMuPDF4LLM 库将 PDF 文件转换为 Markdown 格式。它提供了灵活的配置选项，支持密码保护的 PDF 文件、图像提取、表格提取策略等多种功能。

# 主要特性
- 多种文件来源：支持本地文件路径和网络 URL（可配置请求头）

- 密码保护支持：可打开加密的 PDF 文件

- 两种提取模式：
  - "single"：将整个文档作为一个 Document 对象返回
  - "page"：每页作为一个独立的 Document 对象返回

- 图像提取：可选择提取 PDF 中的图像（需要配置图像解析器）

- 表格提取：支持不同的表格提取策略

- 异步支持：提供同步和异步两种加载方式

# 基本用法示例

```python
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

# 初始化加载器
loader = PyMuPDF4LLMLoader(
    file_path="./document.pdf",      # PDF 文件路径
    mode="page",                      # 按页提取模式
    password=None,                    # PDF 密码（如果需要）
    pages_delimiter="\n\f",           # 单文档模式下的页面分隔符
)

# 同步加载文档
documents = loader.load()

# 惰性加载（适用于大文件）
for doc in loader.lazy_load():
    print(doc.page_content[:100])    # 打印前100个字符
    print(doc.metadata)               # 打印元数据

# 异步加载文档
docs = await loader.aload()
```



# 初始化参数说明

| 参数                   | 类型                        | 说明                                                |
| :--------------------- | :-------------------------- | :-------------------------------------------------- |
| `file_path`            | `Union[str, PurePath]`      | PDF 文件路径（本地或网络 URL）                      |
| `headers`              | `Optional[dict]`            | HTTP 请求头（用于下载网络文件）                     |
| `password`             | `Optional[str]`             | PDF 密码（用于加密文件）                            |
| `mode`                 | `Literal["single", "page"]` | 提取模式："single"（整个文档）或 "page"（按页）     |
| `pages_delimiter`      | `str`                       | 单文档模式下的页面分隔符，默认 `"\n\f"`             |
| `extract_images`       | `bool`                      | 是否提取图像，默认 `False`                          |
| `images_parser`        | `Optional[BaseBlobParser]`  | 图像解析器，当 `extract_images=True` 时必须提供     |
| `**pymupdf4llm_kwargs` | `dict`                      | 传递给底层 `pymupdf4llm.to_markdown` 函数的其他参数 |

# 返回值

`load()`、`lazy_load()` 和 `aload()` 方法返回 `Document` 对象列表，每个对象包含：

- `page_content`：Markdown 格式的 PDF 内容
- `metadata`：文档元数据（如页码、文件路径等）

# 重要限制

1. **启用图像提取时的限制参数**（不能与 `extract_images=True` 同时使用）：
   - `ignore_images`
   - `ignore_graphics`
   - `write_images`
   - `embed_images`
   - `image_path`
   - `filename`
2. **始终禁止使用的参数**（与加载器内部逻辑冲突）：
   - `page_chunks`
   - `extract_words`
   - `show_progress`