#!/usr/bin/python
#-*-coding:utf-8-*-

from unrar import rarfile
from wordChangeTxt import Translate
import urllib2, urllib, re, time, os, cookielib, inspect, codecs

class Task:

	#登录的用户名和密码
	username = "cqliwei321"
	password = "liwei123"
	url="http://learning.cmr.com.cn/student/acourse/HomeworkCenter/index.asp?courseid=zk103b"
	previous_cookie = ""

	def __init__(self):
		self.run()

	def getHtmlSource(self, url, username, password, data = {}):
	    try:
	    	#建立带有cookie的opener	
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
			# post数据
	        if data:
				print self.previous_cookie
				headers = { 
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'Accept-Language': 'zh-CN,zh;q=0.8',
					'Connection': 'keep-alive',
					'Content-Type': 'application/x-www-form-urlencoded',
					'Cookie':self.previous_cookie,
					'Referer':'http://learning.cmr.com.cn',
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
				}
				data = urllib.urlencode(data)
				#self.previous_cookie = ''
				url = urllib2.Request(url, data, headers)
			
			#urllib2.urlopen 使用上面的opener.  
	        ret = urllib2.urlopen(url)
	        self.previous_cookie = ''
	        for index, cookie in enumerate(cookie):
	        	self.previous_cookie += cookie.name+'='+cookie.value+';'
	        
	        return ret.read()
	    except urllib2.HTTPError, e:
	        if e.code == 401:
	           return "authorization failed"
	        else:
	            raise e
	    except:
	        return None

	def downloadTask(self, html):
		regex_content = re.compile(
	            '<div.*?class="button_blue2".*?href=\"(.+?)\"',
	            re.S)
		items = re.findall(regex_content, html)
		print "downloading with urllib"
		filedir_child  = os.path.join(self.script_path(),"task")  #解压后放入的目录
		filedir  = os.path.join(filedir_child,"task_"+time.strftime('%Y%m%d%H%I%S'))  #解压后放入的目录
		if not os.path.isdir(filedir_child): os.mkdir(filedir_child)  
		if not os.path.isdir(filedir): os.mkdir(filedir)
		rar_path = os.path.join(filedir,"task.rar")
		print items[0]+'=======>'+rar_path #下载地址
		urllib.urlretrieve(items[0], rar_path)
		print "download finish!"
		print "unrar......!"
		file = rarfile.RarFile(rar_path)  #这里写入的是需要解压的文件，别忘了加路径
		file.extractall(filedir)  #这里写入的是你想要解压到的文件夹
		print "unrar finish!"
		answer_path = Translate(filedir)
		print answer_path
		#返回答案结果
		
		answer = open(answer_path,'r')
		#answer = open(os.path.join(script_path(),"task\\task_20171011200841\\data\\ZK133A.txt"),'r')
		#print(answer.readlines().encode('utf8'))
		reader = codecs.getreader('gbk')(answer)
		return reader.read()
		
	def get_question(self, answer_data, task_html, task_url):
		#匹配问题列表
		task_key_word = u'做作业'
		regex_content = re.compile(
	            '<div.*?class=\"button_red\".*?<a.*?href=\"(.+?)\".*?class=\"a\_white\".*?>'+task_key_word.encode('gbk')+'</a>',
	            re.S)
		items = re.findall(regex_content, task_html.decode('gbk').encode('gbk'))
		if not (items):
			print u'该科目作业已完成了'
		for item in items:
			#匹配单个问题url
			question_html = self.getHtmlSource(task_url+item, self.username, self.password)
			question_regex = u'【(.*?)】'
			regex_content = re.compile(
	            question_regex.encode('gbk'),
	            re.S)
			question_num_items = re.findall(regex_content, question_html.decode('gbk').encode('gbk'))
			answer = {}
			for question_num_item in question_num_items:
				#匹配问题答案
				answer_regex = u'案】'
				regex_content = re.compile(
					question_num_item+'.*?'+answer_regex.encode('gbk')+'([A-Z])',
					re.S)
				answer_items = re.findall(regex_content, answer_data.encode('gbk'))
				answer[question_num_item] = answer_items[0]
				
			#获取提交答案路径
			regex_content = re.compile(
	            '<form.*?id="form1".*?name="form1".*?action="(.*?)"',
	            re.S)
			post_question_url_items = re.findall(regex_content, question_html.decode('gbk').encode('gbk'))
			post_question_url = task_url+post_question_url_items[0]
			#创建post体
			data = answer
			data['CourseID'] = re.findall(re.compile('<input.*?name=\"CourseID\".*?value=\"(.*?)\"',re.S),question_html)[0]
			data['PMID']     = re.findall(re.compile('<input.*?name=\"PMID\".*?value=\"(.*?)\"',re.S),question_html)[0]
			data['tmpSID']   = re.findall(re.compile('<input.*?name=\'tmpSID\'.*?value=\'(.*?)\'',re.S),question_html)[0]
			data['strStandardScore'] = re.findall(re.compile('<input.*?name=\'strStandardScore\'.*?value=\'(.*?)\'',re.S),question_html)[0]
			#post提交答案
			#test_url = 'http://192.168.92.129/Welcome/test11'
			print u'延迟10秒提交答案...'
			time.sleep(10)
			result = self.getHtmlSource(post_question_url, self.username, self.password, data)
			print data
			print self.getScore(result)

		print u'该科目作业已全部完成！！'

	def getScore(self, html):
		regex_content = re.compile(
	            '<div.*?class=\"line1\".*?>.*?<p>(.*?)</p>',
	            re.S)
		items = re.findall(regex_content, html.decode('gbk').encode('gbk'))
		print items[0]


	def script_path(self):
		caller_file = inspect.stack()[1][1]         # caller's filename
		return os.path.abspath(os.path.dirname(caller_file))# path

	def run(self):

		html = self.getHtmlSource(self.url, self.username, self.password)
		#print html
		items = regex_content = re.compile(
	            '<iframe.*?id="iframe".*?src=\"(.+?)\"',
	            re.S)
		items = re.findall(regex_content, html)
		task_url = items[0]
		print task_url
		task_url_items = regex_content = re.compile(
	            '(.*?\/.*?)[^\/]*\.asp.*?',
	            re.S)
		task_url_items = re.findall(regex_content, self.url)
		task_html = self.getHtmlSource(task_url_items[0]+task_url, self.username, self.password)
		answer_data = self.downloadTask(task_html)
		self.get_question(answer_data,task_html,task_url_items[0])

	def __del__(self):
		self.previous_cookie = ''
		

Task()
	
