import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os


def main():

    # 獲取用戶輸入的日期
    user_input = input("請輸入日期 (YYYYMMDD) 或按 Enter 獲取今天的簡報: ")
    # 如果用戶沒有輸入日期，則使用當前日期
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    # 獲取每日簡報
    daily_brief = get_daily_brief(user_input)

    # 將每日簡報保存到桌面
    save_to_markdown(daily_brief, user_input)


def get_daily_brief(date):
    """
    獲取端傳媒的每日簡報
    """
    
    url = f"https://theinitium.com/article/{date}-daily-brief"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "無標題"
        
        # 嘗試多種可能的內容選擇器
        content_selectors = [
            'div.article-content',
            'div.content',
            'article',
            'main'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if content:
            # 移除不需要的元素
            for unwanted in content.select('script, style, nav, header, footer'):
                unwanted.extract()
            
            # 將HTML內容轉換為Markdown格式
            paragraphs = content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            text_content = '\n\n'.join([
                f"{'#' * int(p.name[1])} {p.get_text(strip=True)}" if p.name.startswith('h') else p.get_text(strip=True)
                for p in paragraphs
            ])
        else:
            text_content = "無法獲取文章內容"
            
        # 添加調試信息
        print(f"文章標題: {title}")
        print(f"內容長度: {len(text_content)}")
        
        return f"# {title}\n\n{text_content}\n\n[原文鏈接]({url})"
    
    except requests.RequestException as e:
        return f"# 錯誤\n\n獲取日報時發生錯誤: {e}"

# save_to_markdown
def save_to_markdown(content, date):
    """
    將內容保存為Markdown文件到桌面
    """
    # 獲取用戶的家目錄路徑
    home_dir = os.path.expanduser("~")
    # 構建桌面路徑
    desktop_path = os.path.join(home_dir, "Desktop")
    
    # 生成文件名，格式為 YYYYMMDD-daily-brief.md
    filename = f"{date}-daily-brief.md"
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
    main()