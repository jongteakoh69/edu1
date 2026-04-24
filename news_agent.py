import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_naver_news(keyword):
    # 환경 변수에서 키 가져오기
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("에러: 네이버 API 키가 설정되지 않았습니다.")
        return []

    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=5&sort=sim"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get('items', [])
        print(f"성공: {len(items)}개의 뉴스를 찾았습니다.")
        return items
    else:
        print(f"에러: 네이버 API 호출 실패 (상태 코드: {res.status_code})")
        return []

def send_email(news_items, keyword):
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_pw = os.environ.get('SENDER_PW')
    receiver_email = os.environ.get('RECEIVER_EMAIL')

    if not all([sender_email, sender_pw, receiver_email]):
        print("에러: 메일 설정 정보가 부족합니다.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = f"[Daily News] '{keyword}' 관련 뉴스 브리핑"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    body = f"<h3>'{keyword}' 키워드 검색 결과입니다.</h3><br>"
    if not news_items:
        body += "<p>오늘 검색된 새로운 뉴스가 없습니다.</p>"
    else:
        for item in news_items:
            # HTML 태그 제거 및 정리
            title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            body += f"<p><b>{title}</b><br><a href='{item['link']}'>원문 보기</a></p><hr>"

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_pw)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("성공: 메일이 정상적으로 발송되었습니다.")
    except Exception as e:
        print(f"에러: 메일 발송 중 오류 발생 - {e}")

if __name__ == "__main__":
    target_keyword = "데이터베이스 보안" 
    news = get_naver_news(target_keyword)
    send_email(news, target_keyword)
