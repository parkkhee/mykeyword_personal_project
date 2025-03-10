
import pymysql
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import re
from konlpy.tag import Okt
import collections
import time
import schedule
from selenium.webdriver.common.by import By
import json
import sys


class ClovaSummary:
    # Clova Speech invoke URL

    url = 'https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize'
    client_id = "hqc8tqgwkq"
    client_secret = "j2i5KecP8QJ8sr4nUA3JXn1V4VFlWMj3eJZ2p0Tb"

    def req(self, content):
        request_body = {
            "document": {
                "content": content
            },
            "option": {
                "language": 'ko',
                "model": "news",
                "summaryCount": 2,
                "tone": 3
            }
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-NCP-APIGW-API-KEY-ID': self.client_id,
            'X-NCP-APIGW-API-KEY': self.client_secret
        }
        return requests.post(headers=headers,
                             url=self.url,
                             data=json.dumps(request_body).encode('UTF-8'))


def schedule_fuction():

    try:

        db = pymysql.connect(host='localhost', port=3306, user='root',
                             passwd='qkr96#', db='mykeywordnews', charset='utf8')

        # print(db)

        cursor = db.cursor()

        # if(kw == 1):
        #     cursor.execute("TRUNCATE keyword;")
        select_sql = "SELECT * from user where user_no=%s;"
        select_news_sql = "SELECT user_key, user_no from nate_keyword where user_no=%s;"
        select_cnt = "SELECT count(*) from mykeywordnews.user;"

        insert_sql = "UPDATE naver_keyword SET naver_news_url1=%s, naver_news_word1_1=%s, naver_news_word1_2=%s, naver_news_url2=%s, naver_news_word2_1=%s, naver_news_word2_2=%s, naver_news_url3=%s, naver_news_word3_1=%s, naver_news_word3_2=%s, naver_news_url4=%s, naver_news_word4_1=%s, naver_news_word4_2=%s, naver_word_cnt1=%s, naver_word_cnt2=%s, naver_word_cnt3=%s, naver_word_cnt4=%s, naver_summary1=%s, naver_summary2=%s, naver_summary3=%s, naver_summary4=%s WHERE user_no = %s and user_key = %s;"

        cursor.execute(select_cnt)
        cnt_sql = cursor.fetchall()
        print(cnt_sql[0][0])

        for user_num in range(1, int(cnt_sql[0][0]+1)):

            time.sleep(4)

            user_num = int(user_num)
            print(user_num)

            cursor.execute(select_sql, user_num)
            res = cursor.fetchall()
            print(res[0][0])

            cursor.execute(select_news_sql, res[0][0])
            res2 = cursor.fetchall()
            print(res2)

            nate_keyword = []
            nate_keyword.append(res2[0][0])
            nate_keyword.append(res2[1][0])

            for search in nate_keyword:
                print(search)
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option(
                    "excludeSwitches", ["enable-logging"])
                # 크롬 창 숨기는 옵션 추가
                # chrome_options.add_argument("headless")
                dr = webdriver.Chrome(service=Service(
                    ChromeDriverManager().install()), options=chrome_options)

                # url 생성
                url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search

                # articles 리스트 만들기
                #atc_template = ["div.search-result > ul.search-list > li.items >  a.info"]

                # Webdriver에서 네이버 페이지 접속
                dr.get(url)
                time.sleep(1)  # 대기시간 변경 가능

                # 네이버 기사 눌러서 제목 및 본문 가져오기#
                # 네이버 기사가 있는 기사 css selector 모아오기
                a = dr.find_elements(
                    By.CSS_SELECTOR, 'a.info')

                naver_urls = []
                count = 0  # 핸들러 변수(창 바꿀때 사용)

                # 4번째 네이버뉴스 기사에서 끊기 위해서
                acnt = 0

                # 위에서 생성한 css selector list 하나씩 클릭하여 본문 url얻기
                for i in a:
                    # 다음 기사로 넘어가기 위한 conut 변수
                    count += 1
                    i.click()

                # 현재탭에 접근
                    dr.switch_to.window(dr.window_handles[count-1])
                    time.sleep(1)  # 대기시간 변경 가능

                    # 네이버 뉴스 url만 가져오기

                    url = dr.current_url
                    # print(url)

                    # 팝업창 닫기 코드
                    while len(dr.window_handles) != count+1:
                        dr.switch_to.window(
                            dr.window_handles[len(dr.window_handles) - 1])
                        dr.close()

                    if "n.news.naver.com" in url:
                        naver_urls.append(url)
                        acnt += 1
                    elif "entertain.naver.com" in url:
                        naver_urls.append(url)
                        acnt += 1
                    elif "sports.news.naver.com" in url:
                        naver_urls.append(url)
                        acnt += 1
                    else:
                        pass

                    # 다시처음 탭으로 돌아가기(매우 중요!!!)
                    dr.switch_to.window(dr.window_handles[0])

                    if len(naver_urls) == 4:
                        break

                print(naver_urls)
                # driver 종료  원하는 작업 끝났으면 quit()함수로 반드시 종료. 안그러실 background에서 chrome이 계속 리소스를 잡아먹는다.
                dr.quit()

                naverWordCnt = []
                summaryList = []

                # if (len(naver_urls) == 3):
                #     for _ in range(1):
                #         summaryList.append('')
                #         naverWordCnt.append('')
                #         naver_urls.append('')
                # elif(len(naver_urls) == 2):
                #     for _ in range(2):
                #         summaryList.append('')
                #         naverWordCnt.append('')
                #         naver_urls.append('')
                # elif(len(naver_urls) == 1):
                #     for _ in range(3):
                #         summaryList.append('')
                #         naverWordCnt.append('')
                #         naver_urls.append('')

                if naver_urls:

                    ###naver 기사 본문 및 제목 가져오기###

                    # ConnectionError방지
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

                    contents = []

                    # ss리스트 인덱스를 구별하기 위한 변수
                    ss_cnt = 0
                    ss = []

                    for i in naver_urls:
                        original_html = requests.get(i, headers=headers)
                        html = BeautifulSoup(original_html.text, "html.parser")
                        # 검색결과확인시
                        # print(html)

                        # html태그제거
                        edit_pattern1 = '<[^>]*>'

                        # 뉴스 본문 가져오기
                        if "sports.news.naver.com" in i:
                            naver_news_content = html.select(
                                "div.content_area > div.news_end")
                        elif "entertain.naver.com" in i:
                            naver_news_content = html.select(
                                "div.end_body_wrp > div.article_body")
                        elif "n.news.naver.com" in i:
                            naver_news_content = html.select(
                                "div.newsct_body > div#newsct_article > div#dic_area")
                        # 기사 텍스트만 가져오기
                        # list합치기
                        naver_news_content = ''.join(str(naver_news_content))
            # "sports.news.naver.com" in naver_urls:   "n.news.naver.com" in naver_urls:
                        # html태그제거2
                        edit_pattern2 = '[\t|\n]'

                        # html태그제거 및 텍스트 다듬기
                        naver_news_content = re.sub(
                            pattern=edit_pattern1, repl='', string=naver_news_content)
                        naver_news_content = re.sub(
                            pattern=edit_pattern2, repl='', string=naver_news_content)
                        # 크롬에서 플래시 오류가 발생할수 있는데 edit_pattern3를 사용해 오류 우회가능
                        edit_pattern3 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
                        naver_news_content = naver_news_content.replace(
                            edit_pattern3, '')

                        # naver_news_content = naver_news_content.replace(" ", "/")

                        # 크롤링한 기사 요약하기 API
                        WORDS = 1999
                        summary = ""

                        for i in range((len(naver_news_content)//WORDS)+1):
                            # print(i, "번째***********")
                            res = ClovaSummary().req(
                                naver_news_content[WORDS*i:WORDS*(i+1)])
                            rescode = res.status_code
                            if(rescode == 200):
                                # print(str(i) + res.text)
                                summary += json.loads(res.text)["summary"]
                                # summary += res.text["summary"]
                            else:
                                print("first Error : " + res.text)

                        if (len(naver_news_content)//WORDS) > 0:
                            res = ClovaSummary().req(summary)
                            rescode = res.status_code
                            if(rescode == 200):
                                # print(res.text)
                                summary = json.loads(res.text)["summary"]
                            else:
                                print("Error : " + res.text)

                        summaryList.append(summary)
                        print("최종 summary")
                        print(summary)
                        print("-------------------------------")
                        print("-------------------------------")

                        # 형태소 별로 분리해주는 라이브러리
                        nlpy = Okt()

                        nouns = nlpy.nouns(naver_news_content)  # 기사 본문을 명사로 분리

                        # 한자수의 단어 배제
                        for enum, notone in enumerate(nouns):
                            if len(notone) < 2:
                                nouns.pop(enum)

                        # ls = []
                        # ls = naver_news_content.split("/")
                        # ls = ' '.join(ls).split()

                        # 빈도수를 세려면?
                        word_count = collections.Counter(nouns)

                        cnt = 0
                        num = 0
                        i = 1
                        j = 0
                        while(cnt != 2):
                            if word_count.most_common(i)[j][0] == search:
                                j += 1
                                i += 1
                                continue
                            else:
                                ss.append(word_count.most_common(i)[j][0])
                                print('흔한 단어는?: ', ss[ss_cnt], "\n")
                                num = max(num, word_count[ss[ss_cnt]])
                                cnt += 1
                                ss_cnt += 1
                                i += 1
                                j += 1
                        naverWordCnt.append(num)

                        contents.append(naver_news_content)

                    if (len(naver_urls) == 3):
                        for _ in range(1):
                            summaryList.append('')
                            naverWordCnt.append(0)
                            naver_urls.append('')
                            ss.append('')
                            ss.append('')
                    elif(len(naver_urls) == 2):
                        for _ in range(2):
                            summaryList.append('')
                            naverWordCnt.append(0)
                            naver_urls.append('')
                            ss.append('')
                            ss.append('')
                    elif(len(naver_urls) == 1):
                        for _ in range(3):
                            summaryList.append('')
                            naverWordCnt.append(0)
                            naver_urls.append('')
                            ss.append('')
                            ss.append('')
                try:
                    cursor.execute(
                        insert_sql, (naver_urls[0], ss[0], ss[1], naver_urls[1], ss[2], ss[3], naver_urls[2], ss[4], ss[5], naver_urls[3], ss[6], ss[7], naverWordCnt[0], naverWordCnt[1], naverWordCnt[2], naverWordCnt[3], summaryList[0], summaryList[1], summaryList[2], summaryList[3], res2[0][1], search))
                except:
                    pass
            try:
                db.commit()
            except:
                pass
        db.close()
    except:
        pass


# 1초마다 test_fuction을 동작시키자
schedule.every(1).seconds.do(schedule_fuction)

while True:
    schedule.run_pending()
    time.sleep(1)
