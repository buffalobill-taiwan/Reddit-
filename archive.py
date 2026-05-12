#!/usr/bin/env python3
import os
import re
import subprocess
from datetime import datetime, timedelta

PUBLISH_DIR = os.path.join(os.path.dirname(__file__), "publish")
CUTOFF = datetime.now() - timedelta(days=3)


def main():
    if not os.path.exists(PUBLISH_DIR):
        return

    cutoff_str = CUTOFF.strftime("%Y%m%d")

    for fname in os.listdir(PUBLISH_DIR):
        fpath = os.path.join(PUBLISH_DIR, fname)
        if not os.path.isfile(fpath) or not fname.endswith(".md"):
            continue

        match = re.match(r"(\d{8})_", fname)
        if not match:
            continue

        filedate = match.group(1)
        if filedate >= cutoff_str:
            continue

        yearmonth = filedate[:6]
        dest_dir = os.path.join(PUBLISH_DIR, yearmonth)
        os.makedirs(dest_dir, exist_ok=True)

        subprocess.run(["git", "mv", fpath, os.path.join(dest_dir, fname)], check=True)


if __name__ == "__main__":
    main()
