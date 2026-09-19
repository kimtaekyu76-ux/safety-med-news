@echo off
cd /d "C:\Users\prime\Desktop\안전상비약뉴스"
python news_crawler.py
git add .
git commit -m "Auto update"
git push