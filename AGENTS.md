# AGENTS.md

## 專案目標

輸入 subreddit 名稱 → 輸出該版今日熱門文章的正體中文翻譯（Markdown）

## 入口命令

```bash
python -m src main nosleep    # 翻譯 r/nosleep 熱門
python -m src main --help     # 查看選項
```

翻譯結果輸出至 `output/{subreddit}_{timestamp}.md`

## 環境需求

- Python 3.11+
- Ollama 運行中 (`ollama serve`)
- 下載模型: `ollama pull gemma4:26b`（需要 32GB+ VRAM）
- 若記憶體不足，用 `ollama pull gemma4:14b` 或 `ollama pull gemma4:2b`

## 依賴

```bash
pip install requests beautifulsoup4 pyyaml
```

## 架構

```
src/
├── scraper.py      # Reddit JSON API 爬蟲
├── translator.py  # Ollama 翻譯模組
├── main.py        # CLI 入口
└── __init__.py
```

## 技術要點

### Reddit JSON Scraper

無需驗證，使用公開 JSON API：

```python
url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
headers = {"User-Agent": "redditTrans/1.0"}
```

### Ollama Chat API

```python
import ollama

response = ollama.chat(
    model='gemma4:26b',  # 若OOM則自動fallback
    messages=[{
        'role': 'user',
        'content': f'翻譯成正體中文，保留驚悚氛圍：{post_content}'
    }]
)
print(response['message']['content'])
```

### 翻譯 Prompt

```
你是一個專業翻譯師，擅長翻譯恐怖故事。請將以下Reddit貼文翻譯成正體中文，
必須保留：
- 原文的驚悚氛圍和情緒
- 故事的緊湊節奏
- 對話的口語化表達
只輸出翻譯結果，不要解釋。
```

### Markdown 輸出格式

```markdown
# {原始標題}

作者: {author} | 得分: {score} | 連結: {permalink}

---

{翻譯內容}

---
*翻譯自 Reddit r/{subreddit}*
```