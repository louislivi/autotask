#!/usr/bin/python
#-*-coding:gbk-*-

from unrar import rarfile
from wordChangeTxt import Translate
from progressbar import *
from requests.auth import HTTPBasicAuth
import urllib2, urllib, re, time, os, cookielib, inspect, codecs, sys, requests, random, chardet

class Task:

	#登录的用户名和密码
	username = "cqchenshuai"
	password = "cq123456"
	url=""
	previous_cookie = ""
	all_task_url = {}

	def __init__(self):
		#self.username = raw_input("username: ")  
		#self.password = raw_input("password: ")  
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
					print str(item[0])+':剩余'+str(surplus)+'项作业未完成！'
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
					self.all_task_url[str(item[0])] = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/index.asp?courseid="+task_items[0]
					print self.all_task_url
					
				else:
					print str(item[0])+':已完成全部作业'
			else:
				print str(item[0])+':已完成全部作业'
		else:
			print '连接服务器失败，请稍后再试！'
	
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
		if not items:
			print '无法完成主观题！'
			return False
		print items[0]+'=======>'+rar_path #下载地址
		widgets = ['答案下载进度: ', Percentage(), ' ', Bar(marker=RotatingMarker('>-=')),
           ' ', ETA(), ' ', FileTransferSpeed()]
		self.pbar = ProgressBar(widgets=widgets, maxval=100).start()
		urllib.urlretrieve(items[0], rar_path, self.Schedule)
		self.pbar.finish()
		self.pbar = ''
		print "download finish"
		print "unrar...!"
		file = rarfile.RarFile(rar_path)  #这里写入的是需要解压的文件，别忘了加路径
		file.extractall(filedir)  #这里写入的是你想要解压到的文件夹
		print "unrar finish!"
		answer_path = Translate(filedir)
		if not os.path.exists(answer_path):
			notic = "自动转换失败，请将:"+filedir+" 下的word文件，复制为txt文件保存到:"+answer_path+"后按回车键！"
			raw_input(notic)
		print answer_path
		#返回答案结果
		
		#answer = open(answer_path,'r')
		#answer = open(os.path.join(script_path(),"task\\task_20171011200841\\data\\ZK133A.txt"),'r')
		#print(answer.readlines().encode('utf8'))
		# try:
		#reader = codecs.getreader('gbk')(answer)
		reader = codecs.open(answer_path,'r', 'gbk', 'ignore')
		# except Exception, e:
			# if "invalid start byte" in str(e):
		#reader = codecs.getreader()(answer)
		return reader.read()
		#return answer.read()
	
	def whichEncode(text):
		text0 = text[0]
		try:
			text0.decode('utf8')
		except Exception, e:
			if "unexpected end of data" in str(e):
				return "utf8"
			elif "invalid start byte" in str(e):
				return "gbk_gb2312"
			elif "ascii" in str(e):
				return "Unicode"
		return "utf8"
	
		
	def Schedule(self,a,b,c):
		'''''
		a:已经下载的数据块
		b:数据块的大小
		c:远程文件的大小
		'''
		per = 100.0 * a * b / c
		if per > 100 :
			per = 100
		self.pbar.update(per)
		
	def get_question(self, answer_data, task_html, task_url):
		#匹配问题列表
		task_key_word = '做作业'
		regex_content = re.compile(
	            '<div.*?class=\"button_red\".*?<a.*?href=\"(.+?)\".*?class=\"a\_white\".*?>'+task_key_word+'</a>',
	            re.S)
		items = re.findall(regex_content, task_html)
		if not (items):
			print '该科目作业已完成了'
		for item in items:
			#匹配单个问题url
			question_html = self.getHtmlSource(task_url+item, self.username, self.password)
			question_regex = '【(.*?)】'
			regex_content = re.compile(
	            question_regex,
	            re.S)
			question_num_items = re.findall(regex_content, question_html)
			answer = {}
			#print chardet.detect(answer_data)
			for question_num_item in question_num_items:
				
				#匹配问题答案
				answer_regex = u'案】'
				
				question_regex = question_num_item+'[^'+u'案'+']*'+answer_regex+'([A-Z])'
				regex_content = re.compile(
					question_regex,
					re.S)
				#单项选择题
				radio_items = re.findall(regex_content, answer_data)
				if radio_items:
					answer[question_num_item] = radio_items[0]
				else:
					#判断题
					regex_content = re.compile(
					question_num_item+'[^'+u'案'+']*'+answer_regex+u'(正确|错误)',
					re.S)
					judge_items = re.findall(regex_content, answer_data)
					if judge_items:
						if judge_items[0] == u'正确':
							answer[question_num_item] = 1
						else:
							answer[question_num_item] = 0
					else:
						#多项选择题
						regex_content = re.compile(
						question_num_item+'[^'+u'案'+']*'+answer_regex+'([A-Z\,]*)',
						re.S)
						checkbox_items = re.findall(regex_content, answer_data)
						if checkbox_items:
							answer[question_num_item] =  checkbox_items[0].split(',')
						else:
							answer[question_num_item] =  ''
			#获取提交答案路径
			regex_content = re.compile(
	            '<form.*?id="form1".*?name="form1".*?action="(.*?)"',
	            re.S)
			post_question_url_items = re.findall(regex_content, question_html)
			post_question_url = task_url+post_question_url_items[0]
			#创建post体
			data = answer
			data['CourseID'] = re.findall(re.compile('<input.*?name=\"CourseID\".*?value=\"(.*?)\"',re.S),question_html)[0]
			data['PMID']     = re.findall(re.compile('<input.*?name=\"PMID\".*?value=\"(.*?)\"',re.S),question_html)[0]
			data['tmpSID']   = re.findall(re.compile('<input.*?name=\'tmpSID\'.*?value=\'(.*?)\'',re.S),question_html)[0]
			data['strStandardScore'] = re.findall(re.compile('<input.*?name=\'strStandardScore\'.*?value=\'(.*?)\'',re.S),question_html)[0]
			#post提交答案
			#test_url = 'http://192.168.92.129/Welcome/test11'
			print '延迟10秒提交答案...'
			time.sleep(10)
			result = self.getHtmlSource(post_question_url, self.username, self.password, data)
			print data
			print self.getScore(result)

		print '该科目作业已全部完成！！'

	def getScore(self, html):
		regex_content = re.compile(
	            '<div.*?class=\"line1\".*?>.*?<p>(.*?)</p>',
	            re.S)
		items = re.findall(regex_content, html)
		if not items:
			print '提交数据失败！'
			return False
		print items[0]


	def script_path(self):
		caller_file = inspect.stack()[1][1]         # caller's filename
		return os.path.abspath(os.path.dirname(caller_file))# path

	def run(self):
		self.getNotTask();
		for index in self.all_task_url:
			print '开始完成'+index+'课程...'
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
			task_url_items = regex_content = re.compile(
					'(.*?\/.*?)[^\/]*\.asp.*?',
					re.S)
			task_url_items = re.findall(regex_content, self.url)
			task_html = self.getHtmlSource(task_url_items[0]+task_url, self.username, self.password)
			answer_data = self.downloadTask(task_html)
			if not answer_data:
				continue
			self.get_question(answer_data,task_html,task_url_items[0])
		# testurl = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/Model.asp?courseid=zk134a&isshow=1"
		# task_html = self.getHtmlSource(testurl, self.username, self.password)
		# answer_path = "C:\\Users\\李巍\\Desktop\\pythontask\\autotask\\task\\task_20171016200850\\data\\ZK134A.txt"
		# reader = codecs.open(answer_path,'r', 'gbk', 'ignore')
		# test_data = reader.read()
		# testurl = "http://learning.cmr.com.cn/student/acourse/HomeworkCenter/";
		# self.get_question(test_data,task_html,testurl)

	def __del__(self):
		self.previous_cookie = ''
		

Task()
	
