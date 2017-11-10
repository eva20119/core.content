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
import cPickle as pickle 
reload(sys)
sys.setdefaultencoding('utf-8')


class Manage_list(BrowserView):
    template = ViewPageTemplateFile('template/manage_list.pt')
    
    def get_data(self):
        web_user = api.user.get_current().getProperty('fullname')

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
                sql = """SELECT title,content,time,url,who_release FROM news LIMIT 3"""
                cursor.execute(sql)
                result = cursor.fetchall()
                data = []
                for item in result:
                    item['title'] = item['title'].encode('utf-8')
                    item['time'] = item['time'].strftime('%Y-%m-%d %H:%M:%S')
                    item['content'] = item['content'].encode('utf-8')
                    item['url'] = item['url'].encode('utf-8')

                    members= item['who_release'].encode('utf-8').split(',')
                    for member in members:
                        if(member == web_user):
                            item['btn_content'] = '再次發佈'
                            break
                        else:
                            item['btn_content'] = '發佈'
                    data.append(item)
                    
                return data
            connection.commit()

        finally:
            connection.close()

    def __call__(self):
        return self.template()


class Release_news(BrowserView):
    def __call__(self):
        self.news_title = safe_unicode(self.request.get('news_title'))
        self.news_content = safe_unicode(self.request.get('news_content'))
        self.btn_content = self.request.get('btn_content')
        self.news_url = self.request.get('news_url')
        self.web_user = api.user.get_current().getProperty('fullname')

        self.target = 'https://www.weibo.com/login.php'

        self.release = self.release_news(self.target, self.news_title, self.news_content, self.btn_content, self.news_url, self.web_user)

    def release_news(self, target, news_title, news_content, btn_content , news_url, web_user):
        self.count(web_user)
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('window-size=1200,1100');
        # chromedriver = "/usr/local/share/chromedriver"
        # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver)
        # data_list = []

        # browser.maximize_window()

        # browser.implicitly_wait(10)
        # browser.get(target)

        # print browser.title

        # username = browser.find_element_by_id('loginname')
        # pwd = browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')
        # print ('輸入帳號密碼')
        # username.send_keys('ah13441673@gmail.com')
        # time.sleep(1)
        # pwd.send_keys('hn13441673')
        # time.sleep(1)
        # browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
        # print ('按下登入紐')
        # # 數入訊息
        # time.sleep(2)
        # print ('輸入訊息')
        # send_box = browser.find_element_by_xpath('//textarea[@class="W_input"]')

        # send_box.send_keys(news_title)
        # time.sleep(1)
        # send_box.send_keys(news_content)
        # time.sleep(1)
        # # 按下送出訊息
        # browser.find_element_by_xpath('//div[@id="v6_pl_content_publishertop"]/div/div[3]/div[1]/a').click()
        
        # browser.quit()
        # if btn_content == "發佈":
        #     self.insert_web_user(news_url, web_user)

        # print('發佈完成')

    def insert_web_user(self, news_url, web_user):
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
                
                who_release = self.get_who_release(news_url)
                
                if who_release[0]['who_release']=='':
                    who_release[0]['who_release']+='{}'.format(web_user)
                else:
                    who_release[0]['who_release']+=',{}'.format(web_user)

                result = who_release[0]['who_release']
                sql = """UPDATE news SET who_release='{}' WHERE url='{}'""".format(result, news_url)
                cursor.execute(sql)
                
            connection.commit()

        finally:
            connection.close()
        
    def get_who_release(self, news_url):
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
                
                sql = """SELECT who_release FROM news where url ='{}' """.format(news_url)
                cursor.execute(sql)
                who_release = cursor.fetchall()
                return who_release                
            connection.commit()

        finally:
            connection.close()
    
    def check_count(self, web_user):
        filename=web_user+'pickle'
        try:
            f = open (filename,'rb')
            count = pickle.load(f)
            if count<5:
                self.release_news(self.target, self.news_title, self.news_content, self.btn_content, self.news_url, self.web_user)
                count+=1
                pickle.dump(count)
        except:
            f = open(filename,'wb')
            f.close()
            self.check_count()