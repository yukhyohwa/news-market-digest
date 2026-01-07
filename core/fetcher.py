# rss_fetcher.py
import feedparser
from urllib.parse import urlparse
from datetime import datetime
from time import mktime

def get_source_name(feed_url):
    """从 feed URL 中提取一个可读的来源名称。"""
    parsed_url = urlparse(feed_url)
    domain = parsed_url.netloc.replace("www.", "")
    try:
        # 返回域名中的主要部分 (例如 'nytimes' from 'cn.nytimes.com')
        return domain.split('.')[-2] if domain.count('.') > 1 else domain.split('.')[0]
    except IndexError:
        return domain

def fetch_feed(feed_url):
    """
    抓取单个 RSS/Atom 源并解析，返回一个包含文章信息的列表。
    使用 feedparser 库。
    """
    print(f"  - 正在抓取: {feed_url}")
    try:
        # feedparser 会自动处理抓取和解析
        feed = feedparser.parse(feed_url)
        
        # 检查解析是否出错
        if feed.bozo:
            # Bozo bit is set if the feed is not well-formed. 
            # We can still try to process it, but log a warning.
            print(f"    ⚠️ 警告: 源格式可能不规范: {feed_url}, Bozo 错误: {feed.bozo_exception}")

        source_name = get_source_name(feed_url)
        articles = []
        
        for entry in feed.entries:
            # feedparser 会自动将不同格式的日期转换为统一的 struct_time
            published_dt = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_dt = datetime.fromtimestamp(mktime(entry.updated_parsed))

            # feedparser 会将摘要放在 'summary' 或 'description'
            summary = entry.get('summary', entry.get('description', ''))

            articles.append({
                'title': entry.get('title', 'N/A'),
                'link': entry.get('link', 'N/A'),
                'summary': summary,
                'published': published_dt,
                'source_name': source_name,
            })
            
        print(f"    => 成功抓取 {len(articles)} 篇文章。")
        return articles
        
    except Exception as e:
        print(f"    ❌ 抓取失败: {feed_url}，错误: {e}")
        return []

def fetch_all_feeds(feed_urls):
    """
    抓取列表中的所有 RSS 源，并返回一个包含所有文章的大列表。
    """
    all_articles = []
    print("\n[阶段 1/5] 开始抓取所有 RSS 源...")
    for url in feed_urls:
        articles_from_feed = fetch_feed(url)
        if articles_from_feed:
            all_articles.extend(articles_from_feed)
    print(f"[阶段 1/5] 完成！总共抓取了 {len(all_articles)} 篇文章。")
    return all_articles

# --- 可选的测试代码 ---
if __name__ == '__main__':
    # 注意：直接运行此文件需要 `config/settings.py` 在 correct location
    try:
        from config.settings import RSS_FEEDS
        if RSS_FEEDS:
            # 测试列表中的第一个源
            test_articles = fetch_all_feeds([RSS_FEEDS[0]])
            if test_articles:
                print("\n--- 测试抓取结果 (来自第一个源) ---")
                first_article = test_articles[0]
                print(f"标题: {first_article['title']}")
                print(f"链接: {first_article['link']}")
                print(f"来源: {first_article['source_name']}")
                print(f"发布时间: {first_article['published']}")
                print(f"摘要 (前100字符): {first_article['summary'][:100]}...")
        else:
            print("请在 config.py 的 RSS_FEEDS 列表中添加至少一个 RSS 源。")
    except ImportError:
        print("请确保 config.py 文件存在并且其中定义了 RSS_FEEDS 列表。")
    except Exception as e:
        print(f"测试时发生错误: {e}")
