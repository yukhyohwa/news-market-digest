# main.py
import time
import sys
import argparse
from datetime import datetime, timezone
from tqdm import tqdm

# 捕获导入错误，并提供清晰的指引
try:
    from rss_fetcher import fetch_all_feeds
    from gemini_processor import process_articles_with_gemini
except ImportError as e:
    if "feedparser" in str(e) or "google" in str(e):
        print("❌ 错误: 核心依赖 'feedparser' 或 'google-generativeai' 未安装。")
        print("   请在您的终端中运行以下命令来安装所有必需的库:")
        print("\n   pip install -r requirements.txt\n")
        sys.exit(1)
    else:
        # 抛出其他意想不到的导入错误
        raise e

# 从我们的模块中导入所有需要的函数
from config import RSS_FEEDS, GEMINI_API_KEY
from processor import deduplicate_and_merge_articles, filter_articles
from markdown_generator import write_markdown_file

def run_pipeline(days=None, start_date=None, end_date=None):
    """
    执行完整的新闻聚合、处理和报告生成流程。
    """
    start_time = time.time()
    
    # 检查配置
    if not RSS_FEEDS:
        print("❌ 错误: 'config.py' 中的 RSS_FEEDS 列表为空。请先添加至少一个 RSS 源。")
        return
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 错误: 'config.py' 中的 GEMINI_API_KEY 未配置。请先设置您的 API 密钥。")
        return

    # 流程开始
    print("===================================")
    print("=== 开始执行 RSS 新闻聚合脚本 (Gemini版) ===")
    print("===================================\n")

    # 步骤 1: 抓取所有 RSS 源的文章
    raw_articles = fetch_all_feeds(RSS_FEEDS)
    if not raw_articles:
        print("\n未能抓取到任何文章，脚本终止。")
        return

    # 步骤 2: 筛选指定日期范围内的文章
    filtered_articles = filter_articles(raw_articles, days=days, start_date=start_date, end_date=end_date)
    if not filtered_articles:
        print("\n筛选后没有剩下任何文章，脚本终止。")
        return
        
    # 步骤 3: 使用 Gemini API 处理文章 (翻译、摘要、分类)
    processed_articles = process_articles_with_gemini(filtered_articles)
    if not processed_articles:
        print("\nGemini未能处理任何文章，脚本终止。")
        return

    # 步骤 4: 去重和合并文章
    unique_articles = deduplicate_and_merge_articles(processed_articles)
    
    # 步骤 5: 根据 Gemini 的分类结果进行整理并生成 Markdown
    print("\n[阶段 5/5] 开始根据 Gemini 结果整理分类并生成报告...")
    categorized = { "科技": [], "经济": [], "政治": [], "其他": [] }
    for article in tqdm(unique_articles, desc="整理分类进度"):
        cat = article.get('category', '其他')
        if cat in categorized:
            categorized[cat].append(article)
        else:
            categorized['其他'].append(article)
            
    # 生成 Markdown 文件
    output_file = write_markdown_file(categorized)
    
    print("[阶段 5/5] 分类整理和报告生成完成！")
    for category, items in categorized.items():
        print(f"  - {category}: {len(items)} 篇")
    
    # 流程结束
    end_time = time.time()
    print("\n==============================")
    if output_file:
        print(f"🎉 全部流程执行完毕！")
        print(f"   报告文件: {output_file}")
    else:
        print(f"❗ 流程执行完毕，但报告未生成。")
        
    print(f"   总耗时: {end_time - start_time:.2f} 秒")
    print("==============================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RSS 新闻聚合脚本 (Gemini版)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--days', 
        type=int, 
        default=1,
        help="指定抓取过去几天的文章。默认为 1 天。"
    )
    
    date_format = "%Y%m%d"
    parser.add_argument(
        '--range',
        type=str,
        help=f"指定一个明确的日期范围来抓取文章。\n格式为 'YYYYMMDD-YYYYMMDD'，例如 '20251216-20251217'。\n如果设置此项，'--days' 参数将被忽略。"
    )

    args = parser.parse_args()

    start_date_obj = None
    end_date_obj = None
    days_arg = args.days

    if args.range:
        try:
            start_str, end_str = args.range.split('-')
            start_date_obj = datetime.strptime(start_str, date_format).replace(tzinfo=timezone.utc)
            end_date_obj = datetime.strptime(end_str, date_format).replace(tzinfo=timezone.utc)
            # 如果使用范围，则忽略 --days
            days_arg = None
            print(f"模式: 按日期范围 ({start_str} to {end_str})")
        except ValueError:
            print(f"❌ 错误: 日期范围格式不正确。请使用 'YYYYMMDD-YYYYMMDD' 格式。")
            sys.exit(1)
    else:
        print(f"模式: 按天数 (过去 {days_arg} 天)")

    run_pipeline(days=days_arg, start_date=start_date_obj, end_date=end_date_obj)