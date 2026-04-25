#!/bin/bash

cd /home/nuweb/playground/redditTrans

export PYTHONPATH=/home/nuweb/playground/redditTrans

python3 src/main.py nosleep --limit 5
python3 src/main.py shortscarystories --limit 5

git add output/
git commit -m "Auto translate: $(date '+%Y-%m-%d %H:%M')" || exit 0
git push
