import matplotlib
matplotlib.use('Agg')

import requests
from bs4 import BeautifulSoup
import csv
import html
from datetime import datetime
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

query = "안전상비약 확대"
url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
articles = soup.select("div.news_area")
print(f"수집된 기사 수: {len(articles)}")

pro_keywords = ["편의성", "접근성", "국민 편의", "심야", "공휴일", "약국 부재", "규제 완화"]
con_keywords = ["안전성 우려", "오남용", "부작용", "약사회", "전문가 상담", "신중", "안전 문제"]

def classify(text):
    pro_count = sum(text.count(word) for word in pro_keywords)
    con_count = sum(text.count(word) for word in con_keywords)
    if pro_count > con_count:
        return "확대 찬성 경향"
    elif con_count > pro_count:
        return "확대 반대 경향"
    else:
        return "중립/판단보류"

results = []
for article in articles:
    title_tag = article.select_one("a.news_tit")
    title = title_tag.get_text(strip=True) if title_tag else ""
    link = title_tag["href"] if title_tag else ""

    press_tag = article.select_one("a.press")
    press = press_tag.get_text(strip=True) if press_tag else ""

    date_tag = article.select_one("span.info")
    date = date_tag.get_text(strip=True) if date_tag else ""

    dsc_tag = article.select_one("div.dsc_wrap") or article.select_one("a.dsc_txt_wrap")
    summary = dsc_tag.get_text(strip=True) if dsc_tag else ""

    label = classify(title + " " + summary)
    results.append([date, press, title, summary, label, link])

pro_total = sum(1 for r in results if r[4] == "확대 찬성 경향")
con_total = sum(1 for r in results if r[4] == "확대 반대 경향")
neutral_total = sum(1 for r in results if r[4] == "중립/판단보류")
print(f"찬성 경향: {pro_total}건 / 반대 경향: {con_total}건 / 중립: {neutral_total}건")

with open("안전상비약_뉴스.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["발행일", "언론사", "제목", "요약", "분류", "링크"])
    writer.writerows(results)
print("저장 완료: 안전상비약_뉴스.csv")

labels = ["확대 찬성", "확대 반대", "중립/보류"]
counts = [pro_total, con_total, neutral_total]

plt.figure(figsize=(6, 4))
plt.bar(labels, counts, color=["#4C72B0", "#DD8452", "#999999"])
plt.title("안전상비약 확대 관련 뉴스 찬반 경향")
plt.ylabel("기사 수")
plt.savefig("찬반_그래프.png", dpi=150, bbox_inches="tight")
print("그래프 저장 완료: 찬반_그래프.png")

# 웹페이지(index.html) 생성
updated_time = datetime.now().strftime("%Y-%m-%d %H:%M")

rows_html = ""
for date, press, title, summary, label, link in results:
    css_class = "pro" if label == "확대 찬성 경향" else ("con" if label == "확대 반대 경향" else "")
    rows_html += (
        f'<tr><td>{html.escape(date)}</td><td>{html.escape(press)}</td>'
        f'<td><a href="{html.escape(link)}" target="_blank">{html.escape(title)}</a></td>'
        f'<td class="{css_class}">{html.escape(label)}</td></tr>\n'
    )

page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>안전상비약 확대 뉴스 모니터링</title>
<style>
body {{ font-family: 'Malgun Gothic', sans-serif; margin: 40px; }}
h1 {{ font-size: 22px; }}
.updated {{ color: #666; font-size: 13px; margin-bottom: 20px; }}
img {{ max-width: 500px; display: block; margin-bottom: 30px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 14px; text-align: left; }}
th {{ background: #f5f5f5; }}
.pro {{ color: #4C72B0; font-weight: bold; }}
.con {{ color: #DD8452; font-weight: bold; }}
</style>
</head>
<body>
<h1>안전상비약 확대 뉴스 모니터링</h1>
<div class="updated">마지막 업데이트: {updated_time}</div>
<img src="찬반_그래프.png" alt="찬반 그래프">
<table>
<tr><th>발행일</th><th>언론사</th><th>제목</th><th>분류</th></tr>
{rows_html}
</table>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(page)
print("웹페이지 저장 완료: index.html")