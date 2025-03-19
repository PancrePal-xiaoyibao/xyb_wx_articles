#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从微信公众号文章列表中提取文章信息，并生成两个输出文件：
1. JSON文件：包含文章的标题、URL等信息
2. TXT文件：每行一个URL，方便后续处理
"""

import re
import json
import os
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Dict, Optional

class ArticleExtractor:
    def __init__(self, input_file: str, output_dir: str, json_filename: str = None, url_filename: str = None):
        """
        初始化文章提取器
        
        Args:
            input_file: 输入文件路径（包含文章列表的Markdown文件）
            output_dir: 输出目录
            json_filename: 输出的JSON文件名
            url_filename: 输出的URL文件名
        """
        self.input_file = input_file
        self.output_dir = output_dir
        
        # 从输入文件名生成输出文件名
        input_basename = os.path.basename(input_file)
        input_name = os.path.splitext(input_basename)[0]
        
        self.json_filename = json_filename or f"{input_name}_extracted.json"
        self.url_filename = url_filename or f"extracted_urls_{input_name}.txt"
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def extract_articles(self) -> List[Dict]:
        """从文件中提取文章信息"""
        articles_data = set()
        
        try:
            # 读取文件内容
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式提取标题和URL
            pattern = r'data-link="([^"]+)"\s+data-title="([^"]+)"'
            matches = re.findall(pattern, content)
            
            for link, title in matches:
                if title and link:
                    # 去除URL末尾的#rd
                    link = link.replace('#rd', '')
                    
                    # 提取msgid（如果有）
                    msgid_match = re.search(r'mid=(\d+)', link)
                    msgid = int(msgid_match.group(1)) if msgid_match else None
                    
                    # 创建文章数据字典
                    article_data = {
                        "msgid": msgid,
                        "title": title,
                        "url": link
                    }
                    
                    # 将文章数据转换为JSON字符串，用于去重
                    article_json = json.dumps(article_data, ensure_ascii=False)
                    articles_data.add(article_json)
            
            # 将JSON字符串转回字典
            articles = [json.loads(article) for article in articles_data]
            
            # 按msgid排序
            articles.sort(key=lambda x: x.get("msgid", 0) if x.get("msgid") is not None else 0)
            
            return articles
            
        except Exception as e:
            print(f"提取文章时出错: {str(e)}")
            return []
    
    def save_to_json(self, articles: List[Dict]) -> str:
        """将文章信息保存为JSON文件"""
        json_path = os.path.join(self.output_dir, self.json_filename)
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(articles)} 篇文章信息到 {json_path}")
            return json_path
        except Exception as e:
            print(f"保存JSON文件时出错: {str(e)}")
            return ""
    
    def extract_urls_to_txt(self, articles: List[Dict]) -> str:
        """从文章列表中提取URL并保存到文本文件"""
        url_path = os.path.join(self.output_dir, self.url_filename)
        try:
            # 提取所有URL
            urls = [article['url'] for article in articles if 'url' in article]
            
            # 将URL写入新文件，每行一个
            with open(url_path, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
            
            print(f"已提取 {len(urls)} 个URL到文件: {url_path}")
            return url_path
            
        except Exception as e:
            print(f"提取URL时出错: {str(e)}")
            return ""
    
    def process(self) -> tuple:
        """处理文章提取和保存的完整流程"""
        # 提取文章信息
        articles = self.extract_articles()
        
        if not articles:
            print("未找到任何文章信息")
            return None, None
        
        # 保存为JSON文件
        json_path = self.save_to_json(articles)
        
        # 提取URL并保存为文本文件
        url_path = self.extract_urls_to_txt(articles)
        
        return json_path, url_path

def show_gui():
    """显示图形界面，让用户选择文件和目录"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 提示用户选择输入文件
    messagebox.showinfo("选择文件", "请选择包含微信公众号文章列表的Markdown文件")
    input_file = filedialog.askopenfilename(
        title="选择Markdown文件",
        filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
    )
    
    if not input_file:
        messagebox.showwarning("操作取消", "未选择输入文件，程序将退出")
        return None, None
    
    # 提示用户选择输出目录
    messagebox.showinfo("选择目录", "请选择输出文件保存的目录（默认为当前目录）")
    output_dir = filedialog.askdirectory(title="选择输出目录")
    
    if not output_dir:
        # 如果用户取消选择，使用输入文件所在目录作为默认输出目录
        output_dir = os.path.dirname(input_file)
        messagebox.showinfo("使用默认目录", f"将使用以下目录作为输出目录：\n{output_dir}")
    
    return input_file, output_dir

def main():
    # 检查是否有命令行参数
    parser = argparse.ArgumentParser(description='从微信公众号文章列表中提取文章信息和URL')
    parser.add_argument('-i', '--input', type=str, help='输入文件路径（包含文章列表的Markdown文件）')
    parser.add_argument('-o', '--output', type=str, help='输出目录')
    parser.add_argument('-j', '--json', type=str, help='输出的JSON文件名')
    parser.add_argument('-u', '--url', type=str, help='输出的URL文件名')
    parser.add_argument('--gui', action='store_true', help='使用图形界面')
    
    args = parser.parse_args()
    
    # 如果指定了--gui参数或没有指定输入文件，则使用图形界面
    if args.gui or not args.input:
        input_file, output_dir = show_gui()
        if not input_file:
            return
    else:
        input_file = args.input
        output_dir = args.output or os.path.dirname(input_file)
    
    # 创建文章提取器并处理
    extractor = ArticleExtractor(
        input_file=input_file,
        output_dir=output_dir,
        json_filename=args.json,
        url_filename=args.url
    )
    
    json_path, url_path = extractor.process()
    
    if json_path and url_path:
        print("\n提取完成！")
        print(f"JSON文件: {json_path}")
        print(f"URL文件: {url_path}")
        
        # 显示成功消息框
        try:
            messagebox.showinfo("提取完成", 
                               f"已成功提取文章信息！\n\nJSON文件: {json_path}\n\nURL文件: {url_path}")
        except:
            # 如果无法显示消息框（例如在终端中运行），则忽略错误
            pass
    else:
        print("\n提取失败，请检查输入文件和错误信息。")
        try:
            messagebox.showerror("提取失败", "未能成功提取文章信息，请检查输入文件和错误信息。")
        except:
            pass

if __name__ == "__main__":
    main()