# config.py

# config.py
import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# --- Gemini API 配置 ---
# 从环境变量中读取 API 密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- RSS 源列表 ---
# 在此列表中添加或删除您想订阅的 RSS 源 URL
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theguardian.com/profile/editorial/rss"，
    "https://cn.nytimes.com/rss/", 
    "https://www.csis.org/programs/freeman-chair-china-studies/rss.xml",
]
