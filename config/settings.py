# config.py
import os

# --- RSS 源列表 ---
# 在此列表中添加或删除您想订阅的 RSS 源 URL
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
#   "https://www.theguardian.com/profile/editorial/rss",
    "https://cn.nytimes.com/rss/", 
#   "https://www.france24.com/en/rss",
    "https://www.lefigaro.fr/rss/figaro_actualites.xml",
#   "https://feeds.washingtonpost.com/rss/politics",
    "https://plink.anyfeeder.com/bbc/world"
]
# --- 屏蔽词列表 ---
# 包含以下词汇的文章将被过滤掉 (匹配标题或摘要)
BLOCKED_KEYWORDS = [
    "曲棍球",
    "非洲杯",
    "AFCON",
    "Hockey",
    "法轮功",
    "Falun Gong",
    # 政治/敏感内容
    "爱泼斯坦", "Epstein",
    "教皇利奥", "Pope Leo",
    # 会议/峰会 (TechCrunch 相关)
    "TechCrunch Disrupt",
    "Founders Summit","TechCrunch Founder Summit",
    # 巴黎市政 (Le Figaro 相关)
    "Mairie de Paris", "Hôtel de Ville de Paris", "Paris City Hall","Municipales",
    # 体育类 (法甲、欧冠等)
    "Ligue 1", "Champions League", 
    "Football", "PSG", "Olympique de Marseille", "Real Madrid",
    "Zimbabwe", "NBA",
    "César Awards", "César ceremony", "César du cinéma", "cérémonie des César",
]

# --- 渲染选项 ---
# 是否在报表中显示图片 (默认为 False)
SHOW_IMAGES = False

# --- 翻译选项 ---
# 目标语言 (en 为英文, zh-CN 为中文)
TARGET_LANGUAGE = 'en'

# --- Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL Port
SENDER_EMAIL = "shawnlu91@gmail.com"  # 您的 Gmail 地址
SENDER_PASSWORD = "fgmf fdtt onxv algi" # 16位应用专用密码
RECEIVER_EMAILS = ["shawnlu91@gmail.com"] # 接收报告的邮箱 list

# --- Strategy Configuration / 策略参数配置 ---
STRATEGY_CONFIG = {
    # CEF (Closed-End Funds)
    'cef': {
        'min_discount': -8.0,      # 折价率需小于 -8%
        'max_zscore': -2.0,        # Z-Score 需小于 -2
        'min_volume_usd': 500000,  # 每日成交额需大于 50万 USD
    },
    
    # SPAC (Special Purpose Acquisition Companies)
    'spac': {
        'min_yield': 0.01,         # 年化收益率需大于 1%
        'min_price': 9.5,          # 最低买入价
        'max_price': 9.99,         # 最高买入价
    },
    
    # LOF (Listed Open-Ended Funds)
    'lof': {
        'min_premium_rate': 5.0,   # 溢价率需大于 5%
        'min_fund_share': 20000000, # 基金份额需大于 2000万份 (更稳健)
        'min_turnover': 1000000,    # 成交额需大于 100万元 (保证流动性)
    },
    
    # QDII (Qualified Domestic Institutional Investor)
    'qdii': {
        'min_premium_rate': 5.0,   # 溢价率需大于 5% (T-1 or Realtime)
        'min_fund_share': 20000000, # 基金份额需大于 2000万份
        'min_turnover': 1000000,    # 成交额需大于 100万元
    },

    # CBOND (Convertible Bonds)
    'cbond': {
        'max_dblow': 195.0,        # 双低值小于 195 (价格 + 溢价率*100)
        'max_putback_price': 103.0, # 回售价格接近 100 (103以下)
        'max_putback_years': 2.0,   # 距离回售期/到期小于 2年
    }
}
