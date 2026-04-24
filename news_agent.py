import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. 네이버 뉴스 검색
def get_naver_news(keyword):
    client_id = os.environ['NAVER_CLIENT_ID']
    client_secret = os.environ['NAVER_CLIENT_SECRET']
    
    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=5&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get('items', [])
    return []

# 2. 메일 발송
def send_email(news_items, keyword):
    sender_email = os.environ['SENDER_EMAIL']
    sender_pw = os.environ['SENDER_PW']
    receiver_email = os.environ['RECEIVER_EMAIL']

    msg = MIMEMultipart()
    msg['Subject'] = f"[Daily News] '{keyword}' 관련 뉴스 브리핑"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    body = f"<h3>'{keyword}' 키워드 검색 결과입니다.</h3><br>"
    for item in news_items:
        body += f"<p><b>{item['title']}</b><br>{item['description']}<br><a href='{item['link']}'>원문 보기</a></p><hr>"

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_pw)
        server.sendmail(sender_email, receiver_email, msg.as_string())

if __name__ == "__main__":
    # 리스트 형태로 여러 키워드 설정
    keywords = ["KT 위즈", "KBO 순위"] 
    
    all_news = []
    for kw in keywords:
        news_items = get_naver_news(kw)
        # 검색 결과 상단에 어떤 키워드의 뉴스인지 표시 추가
        for item in news_items:
            item['title'] = f"[{kw}] {item['title']}"
        all_news.extend(news_items)
        
    if all_news:
        send_email(all_news, ", ".join(keywords))
