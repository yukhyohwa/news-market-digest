# check_models.py
from google import genai
from config import GEMINI_API_KEY

try:
    print("正在通过最新 SDK 初始化 Gemini Client...")
    # 初始化客户端
    client = genai.Client(api_key=GEMINI_API_KEY)

    print("正在获取可用的模型列表...")
    print("-" * 30)
    
    count = 0
    # 使用 client.models.list() 获取模型
    for m in client.models.list():
        # 打印支持生成内容的模型
        print(f"模型名称: {m.name} (支持方法: {m.supported_generation_methods})")
        count += 1
            
    print("-" * 30)
    print(f"总共找到 {count} 个模型。")

except Exception as e:
    print(f"检查模型时发生错误: {e}")
    print("请确保已安装最新包: pip install google-genai")