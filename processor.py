# processor.py
from datetime import datetime, timedelta, timezone
from tqdm import tqdm

def filter_articles(articles, days=None, start_date=None, end_date=None):
    if start_date and end_date:
        start_time = start_date
        end_time = end_date
    else:
        days_to_filter = days if days is not None else 1
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days_to_filter)

    filtered_articles = []
    for article in articles:
        published_time = article.get('published')
        if not published_time:
            filtered_articles.append(article)
            continue
        if published_time.tzinfo is None:
            published_time = published_time.replace(tzinfo=timezone.utc)
        
        if start_time <= published_time <= end_time:
            filtered_articles.append(article)
    return filtered_articles

def deduplicate_and_merge_articles(articles):
    print("\n[阶段 4/5] 开始按 AI 话题标签合并文章...")
    unique_articles = []
    for article in tqdm(articles, desc="合并进度"):
        source_info = {'name': article['source_name'], 'link': article['link']}
        current_topic = article.get('topic_key')
        
        is_duplicate = False
        if current_topic:
            for unique_article in unique_articles:
                if current_topic == unique_article.get('topic_key'):
                    if 'sources' not in unique_article:
                        unique_article['sources'] = [{'name': unique_article['source_name'], 'link': unique_article['link']}]
                    if not any(s['link'] == source_info['link'] for s in unique_article['sources']):
                        unique_article['sources'].append(source_info)
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            new_article = article.copy()
            new_article['sources'] = [source_info]
            unique_articles.append(new_article)
    return unique_articles