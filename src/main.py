import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import scraper
import translator


def sanitize_filename(name: str) -> str:
    """Remove characters illegal for filenames."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip()
    if len(name) > 100:
        name = name[:100]
    return name


def main():
    parser = argparse.ArgumentParser(
        description="翻譯 Reddit 熱門貼文成正體中文"
    )
    parser.add_argument(
        "subreddit",
        nargs="?",
        help="Subreddit 名稱 (不含 r/)",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=10,
        help="要翻譯的貼文數量 (default: 10)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=None,
        help="Ollama 模型名稱 (自動選擇)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="output",
        help="輸出目錄 (default: output)",
    )
    parser.add_argument(
        "--sort",
        "-s",
        type=str,
        default="hot",
        choices=["hot", "new", "top", "rising"],
        help="排序方式 (default: hot)",
    )

    args = parser.parse_args()

    if not args.subreddit:
        parser.print_help()
        return

    subreddit = args.subreddit.strip("/")

    print(f"正在抓取 r/{subreddit} 的 {args.sort} 貼文...")

    try:
        posts = scraper.get_hot_posts(subreddit, limit=args.limit, sort=args.sort)
    except Exception as e:
        print(f"錯誤：無法抓取 Reddit 資料 - {e}", file=sys.stderr)
        sys.exit(1)

    if not posts:
        print(f"警告：找不到任何貼文")
        return

    print(f"找到 {len(posts)} 篇貼文，開始翻譯...")

    model = args.model or translator.find_available_model()
    if not model:
        print("錯誤：找不到可用的 Ollama 模型，請先執行 `ollama pull <model>`", file=sys.stderr)
        sys.exit(1)

    print(f"使用模型: {model}")

    date_str = datetime.now().strftime("%Y%m%d")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    translated_count = 0
    failed_count = 0

    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] 翻譯: {post['title'][:50]}...")

        content = scraper.get_post_content(post)

        if not content.strip():
            print(f"  略過空白貼文")
            continue

        try:
            translation = translator.translate(content, model=model)

            translated_title = translator.translate(post['title'], model=model)
            safe_title = sanitize_filename(translated_title)
            output_file = output_dir / f"{date_str}_{subreddit}_{safe_title}.md"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {post['title']}\n\n")
                f.write(f"作者: {post['author']} | 得分: {post['score']} | ")
                f.write(f"評論數: {post['num_comments']} | ")
                f.write(f"[原文]({post['permalink']})\n\n")
                f.write("---\n\n")
                f.write(translation)
                f.write("\n\n---\n")
                f.write(f"\n*翻譯自 Reddit r/{subreddit}*")

            print(f"  → {output_file.name}")
            translated_count += 1

        except Exception as e:
            print(f"  翻譯失敗: {e}")
            failed_count += 1
            continue

    print(f"\n完成！")
    print(f"  翻譯成功: {translated_count}")
    print(f"  翻譯失敗: {failed_count}")


if __name__ == "__main__":
    main()