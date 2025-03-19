# 微信公众号文章批量提取工具

这个工具用于从微信公众号文章列表中提取文章信息，并生成两个输出文件：
1. JSON文件：包含文章的标题、URL等信息
2. TXT文件：每行一个URL，方便后续处理

## 功能特点

- 支持从微信公众号文章列表的Markdown文件中提取文章信息
- 自动提取文章标题和URL
- 自动去重并按msgid排序
- 生成JSON格式的文章信息文件
- 生成纯文本格式的URL列表文件
- 提供图形界面和命令行两种使用方式

## 如何获取微信公众号文章列表

在使用本工具前，您需要先获取包含文章URL和标题的HTML元素。以下是使用Chrome浏览器获取这些元素的步骤：

1. 在微信中打开公众号的历史文章页面或文章合集页面
2. 将页面分享到电脑，或使用微信网页版打开
3. 在Chrome浏览器中打开该页面
4. 滚动页面直到所有需要的文章都已加载出来（确保全文显示）
5. 按F12键（或右键点击页面并选择"检查"）打开开发者工具
6. 在开发者工具中，点击左上角的"选择元素"按钮（或按Ctrl+Shift+C）
7. 在页面上点击任意一篇文章，然后在开发者工具的元素面板中查看对应的HTML代码
8. 在元素面板中，使用搜索功能（Ctrl+F）搜索"data-link"
9. 找到包含所有文章的容器元素，通常是带有类似"album-content-js"等class的div元素
10. 右键点击该容器元素，选择"复制" > "复制元素"
11. 打开一个文本编辑器（如VS Code、记事本等，不推荐使用飞书等有字数限制的编辑器）
12. 创建一个新的.md文件并粘贴复制的HTML代码
13. 保存该文件，记住这个文件的路径，稍后将作为本工具的输入文件

> **注意**：确保复制的HTML元素包含所有需要提取的文章。如果文章太多，可能需要分批次复制。

## 使用方法

### 图形界面模式

直接运行脚本，将弹出图形界面引导您选择文件和目录：

```bash
python extract_articles_and_urls.py
```

或者在cursor/vscode/trae/windsurf等IDE中直接执行文件更加方便。

## 相关资源

- **飞书文档**（小x宝社区内部）：
  ```
  https://uei55ql5ok.feishu.cn/wiki/J62Nwbl7hiOApikDmvEcB3EUnQc
  ```

- **批量微信公众号下载教学视频**：
  ```
  https://www.vidline.com/share/V0G2HA3AM4/26d6360c6211320cb482f8ca3699ca75
  ```

- **在线工具**：
  ```
  https://changfengbox.top/wechat
  ```


---
## 批量转换为Markdown
提取URL后，您可以使用 webreader_to_markdown.py 脚本将文章批量转换为Markdown格式。

### webreader_to_markdown.py 使用说明
这个脚本通过API将微信公众号文章批量转换为Markdown格式。
 工作原理
1. 利用专业API进行网页内容访问和转换
2. 支持批量处理，大幅提高转换效率
3. 自动处理文章格式，保留原文排版和图片 使用前准备
1. API密钥申请：
   
   - 可以联系Vlinic大佬申请API密钥（可能需要付费）
   - API密钥用于访问转换服务，提高转换质量和速度
2. 环境配置：
   
   - 创建 .env 文件，将API密钥添加到文件中
   ```bash
   touch .env && vim .env
   ```
   - .env 文件格式示例：
  ``` 
  WEB_READER_API_KEY=your_api_key_here
   ```
   - 确保 .env 文件与脚本在同一目录下 使用方法


修改输入文件路径
在使用 batch_webreader_to_markdown.py 前，您需要修改脚本中的输入文件路径：

1. 打开 batch_webreader_to_markdown.py 文件
2. 找到以下代码行（大约在第248行）：
   
   ```python
   url_file = '/Users/qinxiaoqiang/Downloads/公众号下载jina2md/dingxiangyuan_element.md'
    ```
   ```
3. 将路径修改为您自己的HTML元素文件路径，例如：
   
   ```python
   url_file = '/您的用户目录/您的文件路径/您的文件名.md'
    ```
   ```
   
   或者使用相对路径：
   
   ```python
   url_file = os.path.join(current_dir, '您的文件名.md')
    ```
   ```
4. 同样，您也可以修改输出目录（如果需要）：
   
   ```python
   output_dir = os.path.join(current_dir, 'converted_files', '您的公众号名称', current_date)
    ```
   ```


```bash
python webreader_to_markdown.py -i extracted_urls.txt -o output_directory
 ```




参数说明：

- -i, --input : 输入的URL列表文件（使用extract_articles_and_urls.py生成的txt文件）
- -o, --output : 输出目录，用于保存转换后的Markdown文件 优势
- 比手动转换效率高数十倍
- 保留原文格式，包括图片、表格等
- 支持批量处理，适合大量文章的转换需求