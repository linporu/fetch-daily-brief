import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os


def main():
    
    # 獲取可以獲取日報的日期
    valid_date = find_valid_date()
    
    # 獲取日報內
    daily_brief = get_daily_brief(valid_date)
    
    # 將日報內容保存到桌面
    save_to_markdown(daily_brief, valid_date)


def find_valid_date():
    """
    return 可以獲取日報的日期
    """

    current_date = datetime.now()
    try_days = 7 # 設定
    
    # 嘗試獲取日報，若不成功則嘗試至多 try_days 天
    for _ in range(try_days):  
        url = f"https://theinitium.com/article/{current_date.strftime('%Y%m%d')}-daily-brief"
        print(f"嘗試獲取 {current_date.strftime('%Y%m%d')} 的日報內容")  # 記錄嘗試訊息

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            print(f"成功獲取 {current_date.strftime('%Y%m%d')} 的日報內容")  # 記錄成功訊息
            return current_date.strftime('%Y%m%d')  # 返回成功獲取的日期
        except requests.RequestException as e:
            print(f"獲取 {current_date.strftime('%Y%m%d')} 日報時發生錯誤: 「{e}」")  # 記錄錯誤訊息

        # 將日期減去一天
        current_date -= timedelta(days=1)

    # 如果七天內都無法獲取，返回 None
    return None  


def get_daily_brief(date):
    """
    獲取端傳媒的日報網站內容
    """
    if date is None:
        return "# 錯誤\n\n指定時間內無法獲取日報內容"

    url = f"https://theinitium.com/article/{date}-daily-brief"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

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
        
        return f"# {title}\n\n{text_content}\n\n[原文鏈接]({url})"
    
    return "# 錯誤\n\n無法獲取任何日報內容"

def save_to_markdown(content, date):
    """
    將內容保存為Markdown文件到桌面
    """
    home_dir = os.path.expanduser("~")
    desktop_path = os.path.join(home_dir, "Desktop")
    filename = f"{date}-daily-brief.md"
    file_path = os.path.join(desktop_path, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件已保存到: {file_path}")
    except IOError as e:
        print(f"保存文件時發生錯誤: {e}")

if __name__ == "__main__":
    main()