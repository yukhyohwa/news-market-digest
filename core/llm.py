# gemini_processor.py
from google import genai
from google.genai import types
import json
import time
from tqdm import tqdm
from config.settings import GEMINI_API_KEY

MODEL_NAME = "gemini-2.0-flash" 
client = genai.Client(api_key=GEMINI_API_KEY)

def process_articles_with_gemini(articles):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 错误: Gemini API 密钥未配置。")
        return []

    print(f"\n[阶段 3/5] 开始使用 Gemini API ({MODEL_NAME}) 处理文章...")
    processed_articles = []
    
    generate_config = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    )

    for article in tqdm(articles, desc="Gemini 处理进度"):
        content_for_prompt = f"Title: {article['title']}\n\nSummary: {article['summary'][:3000]}"

        # 这里的 {{ }} 是为了转义，防止 Python 报错
        prompt = f"""
        任务：翻译标题、总结、分类并提取话题标签。
        1. translated_title: 简练中文标题。
        2. chinese_summary: 2-3句中文摘要。
        3. category: 分类（仅限：科技、经济、政治、其他）。
        4. topic_key: 精准的中文话题词（如“SpaceX发射”）。相同事件必须获得相同词。

        请严格返回 JSON 格式：
        {{
            "translated_title": "...",
            "chinese_summary": "...",
            "category": "...",
            "topic_key": "..."
        }}

        文章内容：
        ---
        {content_for_prompt}
        ---
        """

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=generate_config
            )
            result = json.loads(response.text)
            if isinstance(result, list): result = result[0]

            new_article = article.copy()
            new_article['translated_title'] = result.get('translated_title', article['title'])
            new_article['translated_summary'] = result.get('chinese_summary', article['summary'])
            new_article['category'] = result.get('category', '其他')
            new_article['topic_key'] = result.get('topic_key') 
            processed_articles.append(new_article)
            time.sleep(2) 

        except Exception as e:
            print(f"\n❗ 处理出错: {e}")
            failed_article = article.copy()
            failed_article['translated_title'] = article['title']
            failed_article['translated_summary'] = article['summary']
            failed_article['category'] = '其他'
            failed_article['topic_key'] = None
            processed_articles.append(failed_article)
            time.sleep(2)

    return processed_articles