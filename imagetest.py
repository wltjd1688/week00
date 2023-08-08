import requests
from bs4 import BeautifulSoup

def check_img_Url(main_url, img_url):
   if img_url.startswith("http"):
      return img_url
   elif img_url.startswith("//"):
      img_url = 'https:' + img_url
   else:
      img_url = main_url + '/' +img_url
   return img_url

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}

while True:
    user_input = input("입력을 하세요 (q 입력 시 종료): ")
    if user_input.lower() == 'q':
        print("프로그램을 종료합니다.")
        break
    else:
        print('ㅋㅋ')
        url_receive = user_input
        data = requests.get(url_receive, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        og_image = soup.select_one('meta[property="og:image"]')
        url_image = og_image['content']
        print(check_img_Url(url_receive, url_image))