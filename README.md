# RSS News Summarizer (Gemini Powered) 🚀

这是一个基于 Google Gemini 2.0 Flash 模型的 RSS 新闻聚合与摘要工具。它能够自动抓取多个 RSS 源，利用 AI 进行翻译、摘要、分类，并生成精美的 Markdown 报告。

## 🌟 项目特点

- **多源聚合**：支持同时抓取多个 RSS/Atom 源。
- **AI 智能处理**：集成 Google Gemini API，自动完成文章翻译（英译中）、核心摘要提取。
- **自动分类**：AI 自动将新闻归类为科技、经济、政治等类别。
- **去重合并**：智能识别相同话题的新闻并进行合并展示。
- **精美报告**：自动生成按类别排序的 Markdown 报告。

## 📁 目录结构

项目采用了标准的模块化层级结构，易于维护和扩展：

```text
rss-news-summarizer/
├── main.py              # 程序入口脚本
├── config/              # 配置模块
│   └── settings.py      # RSS 地址及 API 基础配置
├── core/                # 核心逻辑模块
│   ├── fetcher.py       # RSS 抓取逻辑
│   ├── llm.py           # Gemini API 对接逻辑
│   ├── processor.py     # 数据过滤与去重逻辑
│   └── renderer.py      # Markdown 报告生成逻辑
├── data/                # 数据存放
│   └── output/          # 生成的报告存放目录
├── utils/               # 工具函数
├── .env                 # 环境变量（API Key）
└── requirements.txt     # 项目依赖
```

## 🛠️ 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key
在项目根目录创建 `.env` 文件，并添加您的 Gemini API Key：
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. 配置 RSS 源
编辑 `config/settings.py` 中的 `RSS_FEEDS` 列表，添加您感兴趣的 RSS 地址。

### 4. 运行程序
```bash
# 默认抓取过去 1 天的内容
python main.py

# 抓取过去 7 天的内容
python main.py --days 7

# 抓取指定日期范围
python main.py --range 20260101-20260107
```

## 📄 使用文档
详细使用说明请参考 [USAGE.md](./USAGE.md)。

## 🤝 贡献
欢迎提交 Issue 或 Pull Request 来改进本项目！
