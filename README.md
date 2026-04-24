# Reddit 翻譯

將 Reddit 熱門文章翻譯成正體中文的工具。

## 安裝

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 翻譯 r/nosleep 熱門文章
PYTHONPATH=. python3 src/main.py nosleep

# 指定翻譯數量
PYTHONPATH=. python3 src/main.py nosleep --limit 5

# 指定排序方式
PYTHONPATH=. python3 src/main.py nosleep --sort top
```

## 選項

- `--limit, -n` - 要翻譯的貼文數量 (預設: 10)
- `--sort, -s` - 排序方式: hot, new, top, rising (預設: hot)
- `--model, -m` - Ollama 模型名稱 (自動選擇)
- `--output-dir, -o` - 輸出目錄 (預設: output)

## 輸出

翻譯結果會輸出至 `output/` 目錄，檔名格式：
`{日期}_{版面}_{翻譯後的標題}.md`

## 環境需求

- Python 3.11+
- Ollama 運行中
- 下載翻譯模型：`ollama pull gemma4:26b`

## 支援版面

- r/nosleep - 恐怖故事
- r/shortscarystories - 短篇恐怖故事
- 任意 Reddit 版面