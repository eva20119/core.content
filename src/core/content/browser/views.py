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
import cPickle as pickle

reload(sys)
sys.setdefaultencoding('utf-8')


class Manage_list(BrowserView):
    template = ViewPageTemplateFile('template/manage_list.pt')
    
    def get_data(self):
        web_user = api.user.get_current().getUserName()

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
                sql = """SELECT title,content,time,url,who_release FROM news ORDER BY `time` DESC LIMIT 3"""
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
        if api.user.is_anonymous():
            portal = api.portal.get()
            self.request.response.redirect('%s' % portal.absolute_url())
            api.portal.show_message('請先登入', self.request, 'error')
        else:
            return self.template()


class Release_news(BrowserView):
    def __call__(self):
        self.textarea_content = safe_unicode(self.request.get('textarea_content'))
        self.news_title = safe_unicode(self.request.get('news_title'))
        self.news_content = safe_unicode(self.request.get('news_content'))
        self.btn_content = self.request.get('btn_content')
        self.news_url = self.request.get('news_url')
        self.web_user = api.user.get_current().getUserName()

        self.container = self.save2pickle(self.news_title, self.news_content, self.btn_content, self.news_url, self.web_user, self.textarea_content)

        self.target = 'https://www.weibo.com/login.php'
        print('container:%s'%self.container)
        if self.container < 5:
            self.release_news(self.target, self.web_user)

    def save2pickle(self, news_title, news_content, btn_content , news_url, web_user, textarea_content):

        try:
            with open('/tmp/%s.pickle'%web_user,'rb') as f:
                data = pickle.load(f)
                count = len(data)
                print('裏面有：%s'%count)
            if count < 5:
                with open('/tmp/%s.pickle'%web_user,'wb') as f:
                    data.append({
                                'news_title':news_title,
                                'news_url':news_url,
                                'btn_content':btn_content,
                                'textarea_content':textarea_content,
                                'news_content':news_content
                            })  
                    pickle.dump(data,f)
                    new_count=len(data)
                    print ('新增後裏面有：%s'%new_count)
                    return new_count
            else:
                print('排程以滿')
                return 5
        except:
            # 裏面什麼都沒有
            with open('/tmp/%s.pickle'%web_user,'wb') as f:
                data=[]
                data.append({
                             'news_title':news_title,
                             'news_url':news_url,
                             'btn_content':btn_content,
                             'textarea_content':textarea_content,
                             'news_content':news_content
                        })
                count = len(data)
                pickle.dump(data,f)
                print ('裏面什麼都沒有:%s'%count)
                return count

    def release_news(self, target, web_user):
        user_data = self.get_user_data(web_user)
        user_account = user_data['account']
        user_password = user_data['password']

        with open('/tmp/%s.pickle'%web_user,'rb') as f:
            data = pickle.load(f)
        news_title = data[0]['news_title']
        news_url = data[0]['news_url']
        btn_content = data[0]['btn_content']
        textarea_content = data[0]['textarea_content']
        news_content = data[0]['news_content']

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('window-size=1200,1100');
        # chromedriver = "/usr/local/share/chromedriver"
        # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromedriver)
        browser = webdriver.Chrome()

        browser.maximize_window()

        browser.implicitly_wait(10)
        browser.get(target)

        print browser.title

        username = browser.find_element_by_id('loginname')
        pwd = browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')
        print ('輸入帳號密碼')
        username.send_keys(user_account)
        time.sleep(1)
        pwd.send_keys(user_password)
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()
        print ('按下登入紐')
        # 數入訊息
        time.sleep(2)
        print ('輸入訊息')
        send_box = browser.find_element_by_xpath('//textarea[@class="W_input"]')

        send_box.send_keys(textarea_content)
        send_box.send_keys(u'\ue007')
        time.sleep(1)
        send_box.send_keys(news_title)
        send_box.send_keys(u'\ue007')
        time.sleep(1)
        send_box.send_keys(news_content)
        send_box.send_keys(u'\ue007')
        time.sleep(1)
        # 按下送出訊息
        browser.find_element_by_xpath('//div[@id="v6_pl_content_publishertop"]/div/div[3]/div[1]/a').click()
        time.sleep(3)
        browser.quit()

        if btn_content == "發佈":
            self.insert_web_user(news_url, web_user)
        time.sleep(5)
        with open('/tmp/%s.pickle'%web_user,'wb') as f:
            del data[0]
            pickle.dump(data,f)
        print('發佈完成')

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

    def get_user_data(self, web_user):
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
                
                sql = """SELECT account,password FROM weibo_info WHERE user_name='{}'""".format(web_user)
                cursor.execute(sql)
                result = cursor.fetchone()
                return result
            connection.commit()

        finally:
            connection.close()


class User_data(BrowserView):
    template = ViewPageTemplateFile('template/user_data.pt')
    def __call__(self):
        return self.template()

    def check_user_data(self):
        web_user = api.user.get_current().getUserName()

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
                sql = """SELECT account,password FROM weibo_info WHERE user_name='{}'""".format(web_user)
                cursor.execute(sql)
                result = cursor.fetchone()
                data= []
                if result == None or result['account'] == '':
                    data.append({
                        'account':'請輸入網站帳號',
                        'password':'請輸入網站密碼'
                    })
                    return data
                else:
                    account = result['account']
                    password = result['password']
                    data.append({
                        'account':account,
                        'password':password
                    })
                    return data
            connection.commit()

        finally:
            connection.close()
class Save_user_data(BrowserView):
    def __call__(self):
        
        web_site = self.request.get('web_site')
        account = self.request.get('account')
        password = self.request.get('password')
        auto_release = self.request.get('auto_release')
        ran_or_new = self.request.get('ran_or_new')
        gap = self.request.get('gap')
        user_name = api.user.get_current()
        
        if auto_release == None:
            gap = 0
            ran_or_new = ''

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
                sql = """SELECT user_name FROM {} WHERE user_name='{}'""".format(web_site, user_name)
                cursor.execute(sql)
                result = cursor.fetchone()

                if result == None:
                    sql = """INSERT INTO {}(user_name,account,password,auto_release,ran_or_new,gap) VALUES('{}','{}','{}','{}','{}','{}')""".format(web_site, user_name, account, password, auto_release, ran_or_new, gap)
                else:
                    sql = """UPDATE {} SET account='{}',password='{}',auto_release='{}',ran_or_new='{}',gap='{}' WHERE user_name='{}'""".format(web_site, account, password, auto_release, ran_or_new, gap, user_name)

                cursor.execute(sql)

            connection.commit()

        finally:
            connection.close()

        portal = api.portal.get()
        self.request.response.redirect('%s/user_data' % portal.absolute_url())
        api.portal.show_message('更改成功！', self.request, 'info')
        return