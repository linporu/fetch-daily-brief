import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os


def main():
    """
    本程式用於獲取端傳媒的日報內容，並保存到桌面
    """
    
    # 設定重複嘗試獲取日報的次數
    try_days = 7 

    # 獲取可以獲取日報的日期
    valid_date = find_valid_date(try_days)
    # 若無法獲取日報的日期，則終止程式
    if valid_date is None:  
        print(f"錯誤：無法獲取 {try_days} 天內的日報內容")
        return
    
    # 獲取日報內容、標題、網址
    content, title, url = get_daily_brief(valid_date)
    if content is None:
        print("錯誤: 當天日報無內容")
        return

    # 調整日報內容格式
    formated_daily_brief = format_content(content, title, url)

    # 將日報內容保存到桌面
    save_to_markdown(formated_daily_brief, valid_date)


def find_valid_date(try_days):
    """
    return 可以獲取日報的日期，若無則為 None
    """

    current_date = datetime.now()
        
    # 嘗試獲取日報，若不成功則嘗試至多 try_days 天
    for _ in range(try_days):  
        url = f"https://theinitium.com/article/{current_date.strftime('%Y%m%d')}-daily-brief"
        print(f"嘗試獲取 {current_date.strftime('%Y%m%d')} 的日報內容")  # 記錄嘗試訊息

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.head(url, headers=headers)  # 使用 HEAD 請求檢查網頁是否存在
            response.raise_for_status()
            return current_date.strftime('%Y%m%d')  # 回傳成功獲取的日期 str
        except requests.RequestException as e:
            print(f"嘗試獲取 {current_date.strftime('%Y%m%d')} 的日報內容時發生錯誤: 「{e}」")  # 記錄錯誤訊息

        # 將日期減去一天
        current_date -= timedelta(days=1)

    # 如果七天內都無法獲取，回傳 None
    return None  


def get_daily_brief(date):
    """
    獲取端傳媒的日報網站內容，回傳內容、標題、網址
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

    # 獲取標題
    title = soup.title.string if soup.title else None
    
    # 獲取內容
    # 嘗試多種可能的內容選擇器
    content_selectors = [
        'div.article-content',
        'div.content',
        'article',
        'main'
    ]
    for selector in content_selectors:
        content = soup.select_one(selector)
        """
        我目前的程式中，這一段會導致效能不是很好
        因為這會直接抓整個網頁的內容，而不是先看看網頁是否存在後，篩選並只抓取我要的內容
        """

        if content:
            print(f"成功獲取 {date} 的日報內容")  # 記錄成功訊息
            break
        else:
            content = None

    return content, title, url


def format_content(content, title, url):
    """
    將 HTML 內容轉換為 Markdown 格式
    """

    # 處理內容
    # 移除不需要的元素
    for unwanted in content.select('script, style, nav, header, footer'):
        unwanted.extract()
    
    # 嘗試獲取 OG 圖片 URL，使用其他選擇器
    image_meta = content.find('meta', property='og:image') or content.find('img')
    image_url = image_meta['content'] if image_meta and 'content' in image_meta.attrs else image_meta['src'] if image_meta else None

    # 將 HTML 內容的 subtitle 轉換為 Markdown 格式
    text_content = []
    for p in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        if p.name.startswith('h'):
            text_content.append(f"{'#' * int(p.name[1])} {p.get_text(strip=True)}")
        else:
            text_content.append(p.get_text(strip=True))
    text_content = '\n\n'.join(text_content)
    
    # 處理 title
    # 若無標題，則設定為 "無標題"
    if title is None:
        title = "無標題"

    # 回傳格式化後的日報內容，包含圖片 URL
    return f"# {title}\n\n![圖片]({image_url})\n\n{text_content}\n\n[原文連結]({url})"


def save_to_markdown(content, date):
    """
    將內容保存為 Markdown 文件到桌面
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