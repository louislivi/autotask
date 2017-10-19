# !/usr/bin/python
# -*-coding:gbk-*-

import gevent
from threading import Thread
from unrar import rarfile
from wordChangeTxt import Translate
from progressbar import *
from requests.auth import HTTPBasicAuth
from gevent import monkey; monkey.patch_all()
import urllib2, urllib, re, time, os, cookielib, inspect, codecs, sys, requests, random, msvcrt

u'''
    多线程匹配答案
'''
class AnswerThread(Thread):
    def __init__(self, question_num_item, answer_data):
        Thread.__init__(self)
        self.question_num_item = question_num_item
        self.answer_data = answer_data

    def run(self):
        self.result = Task().find_answer(self.question_num_item, self.answer_data)

    def get_result(self):
        return self.result

u'''
    作业类
'''
class Task:
    # 登录的用户名和密码
    username = ""
    password = ""
    url = "" #作业请求地址
    previous_cookie = "" #cookie
    all_task_url = {} #作业地址

    def __init__(self):
        self.username = raw_input('请输入用户名：')
        self.password = self.pwd_input('请输入密码  : ')
        self.run()

    u'''
        urllib2请求
    '''
    def getHtmlSource(self, url, username, password, data=None):
        try:
            # 建立带有cookie的opener
            cookie = cookielib.CookieJar()
            cookieProc = urllib2.HTTPCookieProcessor(cookie)

            # 创建一个密码管理者
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            # 添加用户名和密码
            password_mgr.add_password(None, url, username, password)
            # 创建了一个新的handler
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)

            # 创建 "opener"
            opener = urllib2.build_opener(handler)
            opener.add_handler(cookieProc)
            # 使用 opener 获取一个URL
            opener.open(url)

            # 安装 opener.
            urllib2.install_opener(opener)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': self.previous_cookie,
                'Referer': 'http://learning.cmr.com.cn',
                'User-Agent': self.randHeaderUserAgent(),
            }
            # post数据
            if data:
                print self.previous_cookie
                data = urllib.urlencode(data)
                url = urllib2.Request(url, data, headers)
            else:
                url = urllib2.Request(url, headers=headers)
            # urllib2.urlopen 使用上面的opener.
            ret = urllib2.urlopen(url)
            self.previous_cookie = ''
            for index, cookie in enumerate(cookie):
                self.previous_cookie += cookie.name + '=' + cookie.value + ';'
            #print '请求完成，等待3秒！'
            #time.sleep(3)
            return ret.read()
        except urllib2.HTTPError, e:
            if e.code == 401:
                print "账号或密码错误！"
                return "authorization failed"
            else:
                raise e
        except:

            return None

    u'''
        随机header用户头
    '''
    def randHeaderUserAgent(self):
        head_user_agent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                           'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                           'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
                           'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11']
        return head_user_agent[random.randrange(0, len(head_user_agent))]

    u'''
        获取未完成作业路径
    '''
    def getNotTask(self):
        url = "http://learning.cmr.com.cn/myCourse/homeworkList.asp"
        print '获取未完成作业列表...'
        html = self.getHtmlSource(url, self.username, self.password)
        regex_content = re.compile(
            '<tr.*?>.*?<td.*?>\s?(.*?)</td>.*?<td.*?>(.*?)</td>.*?<td.*?>(.*?)</td>\s*</tr>',
            re.S)
        items = re.findall(regex_content, html)
        for item in items:
            if item[2].isdigit():
                surplus = int(item[1]) - int(item[2])
                if (surplus) > 0:
                    print str(item[0]) + ':剩余' + str(surplus) + '项作业未完成！'
                    subject_list_url = "http://learning.cmr.com.cn/myCourse/mycourse.asp"
                    subject_list_html = self.getHtmlSource(subject_list_url, self.username, self.password)
                    regex_content = re.compile(
                        '<div.*?class=\"courseTitle\".*?id=\".*?\".*?>.*?<a.*?href=\"(.*?)\".*?>(.*?)</a>',
                        re.S)
                    subject_list_items = re.findall(regex_content, subject_list_html)
                    for subject_list_item in subject_list_items:
                        current_subject = subject_list_item[1][:-1]
                        if current_subject == item[0]:
                            task_url = subject_list_item[0]

                    print task_url
                    task_page = requests.get(task_url, auth=HTTPBasicAuth(self.username, self.password))
                    task_html = task_page.text
                    regex_content = re.compile(
                        '{\'courseid\':\'(.*?)\'}',
                        re.S)
                    task_items = re.findall(regex_content, task_html)
                    if task_items:
                        self.all_task_url[str(
                            item[0])] = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/index.asp?courseid=" + \
                                        task_items[0]
                    else:
                        print '无法完成该科目！'+str(item[0])
                    print self.all_task_url

                else:
                    print str(item[0]) + ':已完成全部作业'
            else:
                print str(item[0]) + ':已完成全部作业'
        else:
            print '已完成全部作业'

    u'''
        密码输入框
    '''
    def pwd_input(self, notic):
        print notic,
        chars = []
        while True:
            newChar = msvcrt.getch()
            if newChar in '\r\n':
                # 如果是换行，则输入结束
                print ''
                break
            elif newChar == '\b':
                # 如果是退格，则删除末尾一位
                if chars:
                    del chars[-1]
                    sys.stdout.write('\b')
                    # 删除一个星号，但是不知道为什么不能执行...
            else:
                chars.append(newChar)
                sys.stdout.write('*')
                # 显示为星号
        return ''.join(chars)

    u'''
        下载答案
    '''
    def downloadTask(self, html):
        regex_content = re.compile(
            '<div.*?class="button_blue2".*?href=\"(.+?)\"',
            re.S)
        items = re.findall(regex_content, html)
        print "downloading with urllib"
        filedir_child = os.path.join(self.script_path(), "task")  # 解压后放入的目录
        filedir = os.path.join(filedir_child, "task_" + time.strftime('%Y%m%d%H%I%S'))  # 解压后放入的目录
        if not os.path.isdir(filedir_child): os.mkdir(filedir_child)
        if not os.path.isdir(filedir): os.mkdir(filedir)
        rar_path = os.path.join(filedir, "task.rar")
        if not items:
            print '无法完成主观题！'
            return False
        print items[0] + '=======>' + rar_path  # 下载地址
        widgets = ['答案下载进度: ', Percentage(), ' ', Bar(marker=RotatingMarker('>-=')),
                   ' ', ETA(), ' ', FileTransferSpeed()]
        self.pbar = ProgressBar(widgets=widgets, maxval=100).start()
        urllib.urlretrieve(items[0], rar_path, self.Schedule)
        self.pbar.finish()
        self.pbar = ''
        print "download finish"
        print "unrar...!"
        file = rarfile.RarFile(rar_path)  # 这里写入的是需要解压的文件，别忘了加路径
        file.extractall(filedir)  # 这里写入的是你想要解压到的文件夹
        print "unrar finish!"
        answer_path = Translate(filedir)
        if not os.path.exists(answer_path):
            notic = "自动转换失败，请将:" + filedir + " 下的word文件，复制为txt文件保存到:" + answer_path + "后按回车键！"
            raw_input(notic)
        print answer_path
        # 返回答案结果

        # answer = open(answer_path,'r')
        # answer = open(os.path.join(script_path(),"task\\task_20171011200841\\data\\ZK133A.txt"),'r')
        # print(answer.readlines().encode('utf8'))
        # try:
        # reader = codecs.getreader('gbk')(answer)
        reader = codecs.open(answer_path, 'r', 'gbk', 'ignore')
        # except Exception, e:
        # if "invalid start byte" in str(e):
        # reader = codecs.getreader()(answer)
        return reader.read()
        # return answer.read()

    u'''
        进度条
    '''
    def Schedule(self, a, b, c):
        u'''''
        a:已经下载的数据块
        b:数据块的大小
        c:远程文件的大小
        '''
        per = 100.0 * a * b / c
        if per > 100:
            per = 100
        self.pbar.update(per)

    u'''
        获取问题，并提交答案
    '''
    def get_question(self, answer_data, task_html, task_url):
        # 匹配问题列表
        task_key_word = '做作业'
        regex_content = re.compile(
            '<div.*?class=\"button_red\".*?<a.*?href=\"(.+?)\".*?class=\"a\_white\".*?>' + task_key_word + '</a>',
            re.S)
        items = re.findall(regex_content, task_html)
        if not (items):
            print '该科目作业已完成了'
        for item in items:
            # 匹配单个问题url
            question_html = self.getHtmlSource(task_url + item, self.username, self.password)
            question_regex = '【([^】]*)】'
            regex_content = re.compile(
                question_regex,
                re.S)
            question_num_items = re.findall(regex_content, question_html)
            answer = {}
            # print chardet.detect(answer_data)
            #多线程匹配问题答案
            ts = [AnswerThread(question_num_item, answer_data) for question_num_item in question_num_items]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
                for key, value in t.get_result().items():
                    answer.setdefault(key, value)
            # 获取提交答案路径
            regex_content = re.compile(
                '<form.*?id="form1".*?name="form1".*?action="(.*?)"',
                re.S)
            post_question_url_items = re.findall(regex_content, question_html)
            post_question_url = task_url + post_question_url_items[0]
            # 创建post体
            data = answer
            data['CourseID'] = \
            re.findall(re.compile('<input.*?name=\"CourseID\".*?value=\"(.*?)\"', re.S), question_html)[0]
            data['PMID'] = re.findall(re.compile('<input.*?name=\"PMID\".*?value=\"(.*?)\"', re.S), question_html)[0]
            data['tmpSID'] = re.findall(re.compile('<input.*?name=\'tmpSID\'.*?value=\'(.*?)\'', re.S), question_html)[
                0]
            data['strStandardScore'] = \
            re.findall(re.compile('<input.*?name=\'strStandardScore\'.*?value=\'(.*?)\'', re.S), question_html)[0]
            # post提交答案
            # test_url = 'http://192.168.92.129/Welcome/test11'
            print '延迟10秒提交答案...'
            time.sleep(10)
            result = self.getHtmlSource(post_question_url, self.username, self.password, data)
            print data
            print self.getScore(result)

        print '该科目作业已全部完成！！'

    u'''
        查找问题答案
    '''
    def find_answer(self, question_num_item, answer_data):
        answer = {}
        # 匹配问题答案
        answer_regex = u'案】'

        question_regex = question_num_item + '[^' + u'案' + ']*' + answer_regex + '([A-Z])'
        regex_content = re.compile(
            question_regex,
            re.S)
        # 单项选择题
        radio_items = re.findall(regex_content, answer_data)
        if radio_items:
            answer[question_num_item] = radio_items[0]
        else:
            # 判断题
            regex_content = re.compile(
                question_num_item + '[^' + u'案' + ']*' + answer_regex + u'(正确|错误)',
                re.S)
            judge_items = re.findall(regex_content, answer_data)
            if judge_items:
                if judge_items[0] == u'正确':
                    answer[question_num_item] = 1
                else:
                    answer[question_num_item] = 0
            else:
                # 多项选择题
                regex_content = re.compile(
                    question_num_item + '[^' + u'案' + ']*' + answer_regex + '([A-Z],[^\n]+)',
                    re.S)
                checkbox_items = re.findall(regex_content, answer_data)
                if checkbox_items:
                    answer[question_num_item] = checkbox_items[0].split(',')
                else:
                    answer[question_num_item] = ''
        return answer

    u'''
        获取作业得分
    '''
    def getScore(self, html):
        regex_content = re.compile(
            '<div.*?class=\"line1\".*?>.*?<p>(.*?)</p>',
            re.S)
        items = re.findall(regex_content, html)
        if not items:
            print '提交数据失败！'
            return False
        return items[0]

    u'''
        获取项目根目录
    '''
    def script_path(self):
        caller_file = inspect.stack()[1][1]  # caller's filename
        return os.path.abspath(os.path.dirname(caller_file))  # path
    u'''
        开始完成各科目作业
    '''
    def work_task(self, index):
        print '开始完成' + index + '课程...'
        self.url = self.all_task_url[index]
        html = self.getHtmlSource(self.url, self.username, self.password)
        if html == None:
            print '服务器异常,请稍后再试！'
            return False
        items = regex_content = re.compile(
            '<iframe.*?id="iframe".*?src=\"(.+?)\"',
            re.S)
        items = re.findall(regex_content, html)
        if not items:
            print '服务器异常,请稍后再试！'
            return False
        task_url = items[0]
        print task_url
        regex_content = re.compile(
            '(.*?\/.*?)[^\/]*\.asp.*?',
            re.S)
        task_url_items = re.findall(regex_content, self.url)
        task_html = self.getHtmlSource(task_url_items[0] + task_url, self.username, self.password)
        answer_data = self.downloadTask(task_html)
        if not answer_data:
            return False
        self.get_question(answer_data, task_html, task_url_items[0])

    u'''
        启动
    '''
    def run(self):
        self.getNotTask()
        #协程执行
        g = [gevent.spawn(self.work_task, url) for url in self.all_task_url]
        gevent.joinall(g)
        # testurl = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/Model.asp?courseid=zk134a&isshow=1"
        # task_html = self.getHtmlSource(testurl, self.username, self.password)
        # answer_path = "C:\\Users\\李巍\\Desktop\\pythontask\\autotask\\task\\task_20171016200850\\data\\ZK134A.txt"
        # reader = codecs.open(answer_path,'r', 'gbk', 'ignore')
        # test_data = reader.read()
        # testurl = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/";
        # self.get_question(test_data,task_html,testurl)


    def __del__(self):
        self.previous_cookie = ''
        os.system('pause')


Task()

