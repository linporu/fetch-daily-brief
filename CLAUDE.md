# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraper that fetches daily brief content from Initium Media and saves it as Markdown files to the user's desktop. The project uses uv for dependency management instead of traditional pip/requirements.txt.

## Key Architecture

- **brief.py**: Main application logic containing the web scraping, content formatting, and file management functionality
- **main.py**: Simple entry point (currently just a hello world placeholder)
- **Project uses uv**: Dependencies managed via pyproject.toml and uv.lock instead of requirements.txt

## Essential Commands

```bash
# Install dependencies
uv sync

# Run the main application
python brief.py

# Run the alternative entry point
python main.py
```

## Core Functionality Flow

1. **Date Discovery**: `find_valid_date()` attempts to find a valid daily brief URL by checking the last 7 days
2. **Content Extraction**: `get_daily_brief()` scrapes the HTML content using multiple CSS selectors for robustness
3. **Format Conversion**: `format_content()` converts HTML to Markdown with title, image, and content
4. **File Operations**: `save_to_markdown()` saves to desktop, `open_file()` auto-opens, interactive deletion prompt

## Web Scraping Details

- Target URL pattern: `https://theinitium.com/article/{YYYYMMDD}-daily-brief`
- Uses fallback CSS selectors: `['div.article-content', 'div.content', 'article', 'main']`
- Includes User-Agent headers to avoid blocking
- Cross-platform file opening support (macOS/Windows/Linux)

## Dependencies

- **requests**: HTTP requests and web scraping
- **beautifulsoup4**: HTML parsing and content extraction
- Requires Python 3.12+