# _*_ coding:utf-8_*_
def crawl_url(url: str) -> tuple:
    """
    爬取URL内容

    Returns:
        (markdown_content, title, domain) 元组
    """
    from urllib.parse import urlparse

    try:
        import requests
        from bs4 import BeautifulSoup

        # 使用requests获取页面内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取主要内容
        title = soup.find('title')
        title_text = title.get_text() if title else "No title"

        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()

        # 获取文本
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # 提取域名
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        markdown_content = f"# {title_text}\n\n来源: {url}\n\n{text}"
        return markdown_content, title_text, domain
    except ImportError:
        print(f"warning: requests或BeautifulSoup未安装，尝试使用crawl4ai")
        try:
            from crawl4ai import AsyncWebCrawler
            import asyncio

            async def crawl():
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(url)
                    return result.markdown

            markdown_content = asyncio.run(crawl())
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            return markdown_content, "Unknown", domain
        except Exception as e:
            print(f"error: crawl4ai处理失败: {e}")
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            return f"无法获取URL内容: {url}\n\n错误: {str(e)}", "Error", domain

print(crawl_url("https://docs.langchain.com/oss/python/langchain/middleware/custom"))