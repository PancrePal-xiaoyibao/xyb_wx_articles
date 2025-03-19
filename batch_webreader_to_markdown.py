#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量处理URL列表文件中的文章，将其转换为Markdown格式
"""

import os
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from coding.webreader_to_markdown import WebReaderToMarkdown
import urllib.parse
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    import html2text
except ImportError:
    import subprocess
    print("正在安装html2text...")
    subprocess.check_call(["pip", "install", "html2text"])
    import html2text

class BatchWebReaderToMarkdown:
    def __init__(self, base_dir: str = None):
        """初始化批量转换器"""
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        # 初始化转换器
        self.converter = WebReaderToMarkdown(base_dir)
        # 加载.env文件
        load_dotenv(os.path.join(base_dir, '.env'))
        # 从.env文件中读取API密钥
        self.api_key = os.getenv('WEB_READER_API_KEY')
        # 设置 Web Reader API 的基础 URL
        self.base_url = "https://api.unifuncs.com/api/web-reader/"

    def format_url(self, url_to_encode: str) -> str:
        """
        将 URL 编码并将其格式化成特定的形式
        
        Args:
            url_to_encode: 需要进行 URL 编码的 URL
            
        Returns:
            格式化后的 URL 字符串
        """
        try:
            # 解析URL为组件
            parsed = urllib.parse.urlparse(url_to_encode)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            # 去除重复的chksm参数，只保留第一个
            if 'chksm' in query_params:
                query_params['chksm'] = [query_params['chksm'][0]]
            
            # 重新构建查询字符串
            new_query = urllib.parse.urlencode(query_params, doseq=True)
            
            # 重新构建完整URL
            clean_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            
            # 对清理后的URL进行编码
            encoded_url = urllib.parse.quote_plus(clean_url)
            
            # 构建最终的API URL
            final_url = f"https://api.unifuncs.com/api/web-reader/{encoded_url}?apiKey={self.api_key}"
            
            # 打印URL进行调试
            print(f"\n原始URL: {url_to_encode}")
            print(f"清理后URL: {clean_url}")
            print(f"编码后URL: {encoded_url}")
            print(f"最终API URL: {final_url}")
            
            return final_url
            
        except Exception as e:
            print(f"URL格式化错误: {str(e)}")
            # 如果出错，尝试直接编码
            encoded_url = urllib.parse.quote_plus(url_to_encode)
            return f"https://api.unifuncs.com/api/web-reader/{encoded_url}?apiKey={self.api_key}"

    def extract_urls_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        从文件中提取所有的微信文章URL和标题
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取到的URL和标题列表
        """
        articles = []
        pattern = r'data-link="([^"]+)"\s+data-title="([^"]+)"'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找所有匹配的URL和标题
                matches = re.findall(pattern, content)
                for url, title in matches:
                    if title and url:
                        # 去除URL末尾的#rd
                        url = url.replace('#rd', '')
                        articles.append({'url': url, 'title': title})
                    
            return articles
        except Exception as e:
            print(f'读取文件时出错: {str(e)}')
            return []

    def get_article_content(self, url: str) -> Optional[str]:
        """
        通过Web Reader API获取文章内容
        
        Args:
            url: 文章URL
            
        Returns:
            文章内容（Markdown格式）或错误信息
        """
        try:
            # 格式化URL
            formatted_url = self.format_url(url)
            print(f"\n访问API URL: {formatted_url}")
            
            # 设置请求头，指定接受大文本
            headers = {
                'Accept': 'text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            # 发送GET请求到API，设置超时时间和允许流式响应
            with requests.get(formatted_url, headers=headers, timeout=30, stream=True) as response:
                # 检查响应状态
                response.raise_for_status()
                
                # 获取响应编码
                response.encoding = response.apparent_encoding or 'utf-8'
                
                # 流式读取全部内容
                chunks = []
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                    if chunk:
                        chunks.append(chunk)
                
                # 合并所有内容
                markdown_content = ''.join(chunks)
                
                # 去除推荐阅读、诊疗经验谈及后续内容
                remove_keywords = [
                    '**推荐阅读**',
                    '推荐阅读',
                    '诊疗经验谈',
                    '继续滑动看下一个',
                    '轻触阅读原文'
                ]
                
                for keyword in remove_keywords:
                    if keyword in markdown_content:
                        markdown_content = markdown_content.split(keyword)[0].strip()
                
                # 添加原始URL信息
                markdown_with_header = f"原始URL: {url}\n\n{markdown_content}"
                
                return markdown_with_header
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return f"API请求异常: {str(e)}"
        except Exception as e:
            print(f"未知错误: {str(e)}")
            return f"获取文章内容时出错: {str(e)}"

    def process_urls(self, articles: List[Dict[str, str]], output_dir: Optional[str] = None) -> None:
        """
        批量处理URL列表，将每个URL对应的文章转换为Markdown
        
        Args:
            articles: 包含URL和标题的字典列表
            output_dir: 输出目录，默认为当前目录下的 markdown_output
        """
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), 'markdown_output')
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        total_articles = len(articles)
        for i, article in enumerate(articles, 1):
            try:
                url = article['url']
                title = article['title']
                print(f'\n处理第 {i}/{total_articles} 个URL: {url}')
                
                # 获取文章内容
                markdown = self.get_article_content(url)  # 这里调用了get_article_content方法
                
                if markdown and not markdown.startswith("API请求失败"):
                    # 清理文件名中的非法字符
                    safe_title = self.converter.clean_filename(title)
                    # 限制文件名长度
                    if len(safe_title) > 50:
                        safe_title = safe_title[:47] + "..."
                    
                    # 使用标题作为文件名
                    filename = f'{safe_title}.md'
                    output_file = os.path.join(output_dir, filename)
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown)
                    print(f'已保存到: {filename}')
                else:
                    print(f'转换失败: {markdown}')  # markdown 变量在失败时包含错误信息
                    
            except Exception as e:
                print(f'处理URL时出错: {str(e)}')
                continue

def main():
    # 设置日志输出
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化转换器
    converter = BatchWebReaderToMarkdown(current_dir)
    
    # URL文件路径 - 使用绝对路径
    url_file = '/Users/qinxiaoqiang/Downloads/公众号下载jina2md/dingxiangyuan_element.md' #这里是你要处理的文件路径，就是元素复制黏贴的markdown文件
    
    # 创建时间目录
    current_date = datetime.now().strftime('%Y%m%d')
    
    # 输出目录
    output_dir = os.path.join(current_dir, 'converted_files', '丁香园', current_date)
    
    if not os.path.exists(url_file):
        print(f'错误：找不到URL文件: {url_file}')
        return
        
    # 提取URL
    urls = converter.extract_urls_from_file(url_file)
    if not urls:
        print('没有找到任何有效的URL')
        return
        
    print(f'共找到 {len(urls)} 个URL')
    
    # 处理URL
    converter.process_urls(urls, output_dir)
    print('\n处理完成！')

if __name__ == '__main__':
    main()
