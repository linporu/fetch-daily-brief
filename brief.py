import os
import platform
import subprocess
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


def main():
    """
    本程式用於獲取端傳媒七日內最近一天的日報內容，並保存到桌面
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
    # 若日報無內容，則終止程式
    if content is None:
        print("錯誤: 當天日報無內容")
        return

    # 調整日報內容格式
    formated_daily_brief = format_content(content, title, url)

    # 將日報內容保存到桌面，並回傳檔案路徑
    file_path, file_name = save_to_markdown(formated_daily_brief, valid_date)

    # 自動開啟日報
    open_file(file_path)
    if file_path is None:
        return

    # 詢問是否刪除檔案
    while True:
        prompt = input(f"是否刪除 {file_name} ？(Y/N)： ").lower()
        if prompt == "y":
            delete_file(file_path, file_name)
            break
        if prompt == "n":
            break
        else:
            print("請輸入 Y 或 N")
            continue


def find_valid_date(try_days):
    """
    回傳可以獲取日報的日期，若無則為 None
    """

    current_date = datetime.now()

    # 嘗試獲取日報，若不成功則嘗試至多 try_days 天
    for _ in range(try_days):
        url = f"https://theinitium.com/article/{current_date.strftime('%Y%m%d')}-daily-brief"
        print(f"嘗試獲取 {current_date.strftime('%Y%m%d')} 的日報內容")  # 記錄嘗試訊息
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.head(url, headers=headers, timeout=5)  # 使用 HEAD 請求檢查網頁是否存在
            response.raise_for_status()
            return current_date.strftime('%Y%m%d')  # 回傳成功獲取的日期 str
        except requests.RequestException as e:
            print(
                f"嘗試獲取 {current_date.strftime('%Y%m%d')} 的日報內容時發生錯誤: 「{e}」"
            )  # 記錄錯誤訊息

        # 將日期減去一天
        current_date -= timedelta(days=1)

    # 如果七天內都無法獲取，回傳 None
    return None


def get_daily_brief(date):
    """
    獲取端傳媒的日報網站內容，回傳內容、標題、網址
    """

    url = f"https://theinitium.com/article/{date}-daily-brief"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }

    # 訪問網站
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # 獲取標題
    title = soup.title.string if soup.title else None

    # 獲取內容
    # 嘗試多種可能的內容選擇器
    content_selectors = ['div.article-content', 'div.content', 'article', 'main']
    for selector in content_selectors:
        content = soup.select_one(selector)

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

    # 處理 title
    # 若無標題，則設定為 "無標題"
    if title is None:
        title = "無標題"

    # 處理內容
    # 移除不需要的元素
    for unwanted in content.select('script, style, nav, header, footer'):
        unwanted.extract()

    # 嘗試獲取 OG 圖片 URL，使用其他選擇器
    image_meta = content.find('meta', property='og:image') or content.find('img')
    image_url = (
        image_meta['content']
        if image_meta and 'content' in image_meta.attrs
        else image_meta['src'] if image_meta else None
    )

    # 將 HTML 內容的 subtitle 轉換為 Markdown 格式
    text_content = []
    for p in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        if p.name.startswith('h'):
            text_content.append(f"{'#' * int(p.name[1])} {p.get_text(strip=True)}")
        else:
            text_content.append(p.get_text(strip=True))
    text_content = '\n\n'.join(text_content)

    # 回傳格式化後的日報內容
    return f"# {title}\n\n![圖片]({image_url})\n\n{text_content}\n\n[原文連結]({url})"


def save_to_markdown(content, date):
    """
    將內容保存為 Markdown 文件到桌面
    """

    # 設定桌面路徑
    home_dir = os.path.expanduser("~")
    desktop_path = os.path.join(home_dir, "Desktop")

    # 設定檔案名稱與路徑
    file_name = f"{date}-daily-brief.md"
    file_path = os.path.join(desktop_path, file_name)

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"日報內容已存檔至: {file_path}")
        return file_path, file_name
    except IOError as e:
        print(f"日報內容存檔時發生錯誤: 「{e}」")
        return None


def open_file(file_path):
    """
    自動開啟指定的檔案，根據作業系統選擇命令
    """
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.Popen(['open', file_path])
        elif platform.system() == "Windows":  # Windows
            subprocess.Popen(['start', file_path], shell=True)
        else:  # Linux 或其他系統
            subprocess.Popen(['xdg-open', file_path])
    except Exception as e:
        print(f"開啟檔案時發生錯誤: 「{e}」")


def delete_file(file_path, file_name):
    """刪除指定路徑的檔案"""
    try:
        os.remove(file_path)
        print(f"日報檔案 {file_name} 已成功刪除")
    except FileNotFoundError:
        print(f"日報檔案 {file_name} 不存在")
    except Exception as e:
        print(f"刪除日報檔案時發生錯誤: {e}")


if __name__ == "__main__":
    main()
