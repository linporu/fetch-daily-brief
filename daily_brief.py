import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_daily_brief(date):
    """
    獲取端傳媒的每日簡報
    """
    # 如果未提供日期，則使用今天的日期
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    url = f"https://theinitium.com/article/{date}-daily-brief"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 發送GET請求到目標URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果請求失敗，這將引發異常
        
        # 使用BeautifulSoup解析HTML內容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 獲取文章標題
        title = soup.title.string if soup.title else "無標題"
        
        # 獲取文章內容（這裡假設內容在class為'article-content'的div中）
        content = soup.find('div', class_='article-content')
        if content:
            # 將HTML內容轉換為Markdown格式
            # 這裡我們只做了一個簡單的轉換，您可能需要更複雜的HTML到Markdown的轉換邏輯
            text_content = content.get_text(separator='\n\n', strip=True)
        else:
            text_content = "無法獲取文章內容"
        
        # 返回Markdown格式的內容
        return f"# {title}\n\n{text_content}\n\n[原文鏈接]({url})"
    
    except requests.RequestException as e:
        return f"# 錯誤\n\n獲取日報時發生錯誤: {e}"

def save_to_markdown(content):
    """
    將內容保存為Markdown文件到桌面
    """
    # 獲取用戶的家目錄路徑
    home_dir = os.path.expanduser("~")
    # 構建桌面路徑
    desktop_path = os.path.join(home_dir, "Desktop")
    
    # 生成文件名，格式為 YYYY-MM-DD-daily-brief.md
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-daily-brief.md"
    # 構建完整的文件路徑
    file_path = os.path.join(desktop_path, filename)
    
    try:
        # 將內容寫入文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已保存到: {file_path}")
    except IOError as e:
        print(f"保存文件時發生錯誤: {e}")

if __name__ == "__main__":
    # 獲取用戶輸入的日期
    user_input = input("請輸入日期 (YYYYMMDD) 或按 Enter 獲取今天的簡報: ")
    # 獲取每日簡報內容
    daily_brief = get_daily_brief(user_input if user_input else None)
    # 將內容保存為Markdown文件
    save_to_markdown(daily_brief)