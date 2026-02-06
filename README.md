# Wenku8 to EPUB Converter

将 [轻小说文库](https://www.wenku8.net) 的 TXT 书籍转换为 EPUB 格式的工具。

## Features

- [x] 从书籍页面 URL 获取书籍信息
- [x] 从目录页面获取章节列表
- [x] 从“插图”章节页获取插图
- [ ] 从书籍页面获取下载链接并下载 TXT 文件
- [ ] 配置退避延迟已避免过快请求导致的 429 错误
- [ ] 配置 {429, 500, 502, 503, 504} 重试次数

## 使用方法

打印卷/章节标题（不生成 EPUB）：

```bash
wenku82epub 3519.txt -u "https://www.wenku8.net/book/3519.htm" --dry-run
```

生成 EPUB：

```bash
wenku82epub 3519.txt -u "https://www.wenku8.net/book/3519.htm" -o output.epub
```

生成带插图的 EPUB：

```bash
wenku82epub 3519.txt -u "https://www.wenku8.net/book/3519.htm" -o output.epub -f
```