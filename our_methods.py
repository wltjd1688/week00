import requests
from bs4 import BeautifulSoup
from datetime import datetime

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}

def extract_image_url(main_url):
    data = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    og_image = soup.select_one('meta[property="og:image"]')
    img_url = og_image['content']
    
    if img_url.startswith("http"):
        return img_url
    elif img_url.startswith("//"):
        img_url = 'https:' + img_url
    else:
        img_url = main_url + '/' +img_url
    return img_url

# 파일 이름 바꾸기 관련 모듈들로..
# 날짜 형식은 무조건 "%Y-%m-%d"
def calcualte_day_left(end_day) :
    today = datetime.today().strftime('%Y-%m-%d')
    now = today.split('-')
    end = end_day.split('-')

    now_year = int(now[0])
    now_month = int(now[1])
    now_day = int(now[2])

    end_year = int(end[0])
    end_month = int(end[1])
    end_day = int(end[2])

    now_date = datetime(now_year, now_month, now_day)
    end_date = datetime(end_year, end_month, end_day)
    print(now_date)
    print(end_date)
    result = end_date - now_date
    print(result)
    day_left = result.days
    if (day_left < 0) :
        day_left = 'expired'
        
    elif (day_left == 0) :
        day_left = '오늘 마감!!'
    else :
        day_left = str(day_left) + '일 남았습니다'
    # print("두 날짜 간의 일수 차이:", result.days)
    # print(day_left)
    return day_left
