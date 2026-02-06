# Wenku8 to EPUB Converter

> [!CAUTION]
> 本项目还处于早期开发阶段，功能不完整且可能存在错误。

将 [轻小说文库](https://www.wenku8.net) 的 TXT 书籍转换为 EPUB 格式的工具。

## Features

- [x] 根据书籍 ID 获取 TXT 格式的书籍内容
- [x] 从书籍页面获取封面、作者和出版商等书籍信息
- [x] 从目录页面获取章节列表
- [x] 从“插图”章节页获取插图
- [ ] 配置退避延迟已避免过快请求导致的 429 错误
- [ ] 配置 {429, 500, 502, 503, 504} 重试次数

## 使用方法

打印卷/章节标题（不生成 EPUB）：

```bash
${EXE} -i <book_id> --dry-run
```

生成 EPUB：

```bash
${EXE} -i <book_id>
# 或者 -o 指定输出文件名
${EXE} -i <book_id> -o output.epub
```

生成带插图的 EPUB：

```bash
${EXE} -i <book_id> -f
```

根据你的环境安装 `wenku82epub` 并替换上述的 `${EXE}`:

1. `pip`: `pip install git+https://github.com/xxacgn/wenku82epub`，替换 `${EXE}` 为 `wenku82epub`。
2. `uvx`: 替换 `${EXE}` 为 `uvx git+https://github.com/xxacgn/wenku82epub`。
3. 从源代码安装（用于开发调试）: 克隆仓库，进入项目目录，执行 `uv sync`，替换 `${EXE}` 为 `wenku82epub`。

## License

MIT License

## 生成式 AI 使用说明

本项目使用了生成式 AI 来辅助开发和文档编写。

本项目目前处于早期开发阶段，可能会有未经人工审阅的 AI 生成代码。若您有任何关于代码质量或功能实现的疑问，请随时提出 issue 或 pull request。
