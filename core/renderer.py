# markdown_generator.py
import datetime
import os

def write_markdown_file(categorized_articles, output_filename=""):
    """
    将分类好的文章写入一个 Markdown 文件，并保存在 'output' 文件夹中。
    """
    print("\n[阶段 5/5] 开始生成 Markdown 文件...")
    
    output_dir = os.path.join("data", "output")
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 如果没有提供文件名，则根据日期自动生成
    if not output_filename:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        output_filename = f"新闻摘要_{date_str}.md"
    
    # 完整的文件路径
    full_path = os.path.join(output_dir, output_filename)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            # 写入主标题
            f.write(f"# 新闻摘要 ({datetime.datetime.now().strftime('%Y年%m月%d日')})\n\n")
            
            # 定义分类的顺序
            categories_order = ["科技", "经济", "政治", "其他"]
            
            for category in categories_order:
                articles = categorized_articles.get(category, [])
                if not articles:
                    continue  # 如果该分类下没有文章，则跳过
                
                # 写入分类标题
                f.write(f"## 📰 {category} ({len(articles)}篇)\n\n")
                
                for article in articles:
                    # 写入文章标题
                    f.write(f"### {article['translated_title']}\n\n")
                    
                    # 写入摘要 (现在使用 translated_summary)
                    if article['translated_summary']:
                        f.write(f"> {article['translated_summary']}\n\n")
                    
                    # 写入来源
                    f.write("**来源:**\n")
                    for source in article['sources']:
                        # 格式: - [来源名称](链接)
                        f.write(f"- [{source['name']}]({source['link']})\n")
                    f.write("\n---\n\n")
        
        print(f"[阶段 5/5] 完成！报告已保存到文件: {full_path}")
        return full_path
    
    except Exception as e:
        print(f"❌ 写入 Markdown 文件时出错: {e}")
        return None
