# -*- coding: utf-8 -*- 
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import pymysql
import time
import os
from selenium import webdriver
import sys
from Products.CMFPlone.utils import safe_unicode
from plone import api

reload(sys)
sys.setdefaultencoding('utf-8')


class Manage_list(BrowserView):
    template = ViewPageTemplateFile('template/manage_list.pt')

    def get_data(self):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                sql = """SELECT title,content,time,url FROM news LIMIT 3"""
                cursor.execute(sql)
                result = cursor.fetchall()
                data = []
                for item in result:
                    item['title'] = item['title'].encode('utf-8')
                    item['time'] = item['time'].strftime('%Y-%m-%d %H:%M:%S')
                    item['content'] = item['content'].encode('utf-8')
                    item['url'] = item['url'].encode('utf-8')
                    
                    # if item['who_release'].encode('utf-8') == "未發佈":
                    #     item['who_release']='btn_hide'
                    # else:
                    #     item['who_release']=''

                    data.append(item)
                
                return data
            connection.commit()

        finally:
            connection.close()

    

    def __call__(self):
        return self.template()


class Release_news(BrowserView):
    def __call__(self):
        
        # self.news_title = safe_unicode(self.request.get('news_title'))
        # self.news_content = safe_unicode(self.request.get('news_content'))
        self.news_url = self.request.get('news_url')
        self.target = 'https://www.weibo.com/login.php'
        # self.release = self.release_news(self.target, self.news_title, self.news_content)

        self.user = api.user.get_current()
        self.who_release = self.insert_who_release(self.user, self.news_url)

    def release_news(self, target, news_title, news_content):
        chromedriver = "/usr/local/share/chromedriver"  
        os.environ["webdriver.chrome.driver"] = chromedriver  
        browser = webdriver.Chrome(chromedriver)
        data_list = []
    
        
        browser.maximize_window()

        browser.implicitly_wait(10)
        browser.get(target)
        
        print browser.title
        
        username = browser.find_element_by_id('loginname')
        pwd = browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')

        username.send_keys('ah13441673@gmail.com')
        time.sleep(1)
        pwd.send_keys('hn13441673')
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
        print ('按下登入紐')
        # 數入訊息
        time.sleep(2)
        print ('輸入訊息')
        send_box = browser.find_element_by_xpath('//textarea[@class="W_input"]')

        send_box.send_keys(news_title)
        time.sleep(1)
        send_box.send_keys(news_content)
        time.sleep(1)
        # 按下送出訊息
        browser.find_element_by_xpath('//div[@id="v6_pl_content_publishertop"]/div/div[3]/div[1]/a').click()
        
        browser.quit()

    def insert_who_release(self, user, news_url):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='henry!QAZ@WSX',
            db='scrapyDB',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with connection.cursor() as cursor:
                sql = """SELECT %s FROM news WHERE url=%s"""

                cursor.execute(sql,('who_release',news_url)
                who_release = cursor.fetchall()
                print who_release
            connection.commit()

        finally:
            connection.close()
        