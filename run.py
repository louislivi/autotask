#!/usr/bin/python
#-*-coding:utf-8-*-

import urllib2
import urllib
import re
import time
import os
from unrar import rarfile
import inspect
from wordChangeTxt import Translate
import codecs
#登录的用户名和密码
username = "cqliwei321"
password = "liwei123"
url="http://learning.cmr.com.cn/student/acourse/HomeworkCenter/index.asp?courseid=zk133a"

def getHtmlSource(url, username, password, data = {}):
    try:
	
		# 创建一个密码管理者  
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()  
        # 添加用户名和密码  
        password_mgr.add_password(None, url, username, password)  
        # 创建了一个新的handler  
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)  
        # 创建 "opener" 
        opener = urllib2.build_opener(handler)  
        # 使用 opener 获取一个URL  
        opener.open(url)  
        # 安装 opener.  
        urllib2.install_opener(opener)  
		# post数据
	if data:
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'# 将user_agent写入头信息
		headers = { 'User-Agent' : user_agent }
		data = urllib.urlencode(data)
		url = urllib2.Request(url, data, headers)
	#urllib2.urlopen 使用上面的opener.  
	ret = urllib2.urlopen(url)
	#print ret.headers
        return ret.read()
    except urllib2.HTTPError, e:
        if e.code == 401:
           return "authorization failed"
        else:
            raise e
    except:
        return None
		
def downloadTask(html):
	# regex_content = re.compile(
            # '<div.*?class="button_blue2".*?href=\"(.+?)\"',
            # re.S)
	# items = re.findall(regex_content, html)
	# print "downloading with urllib"
	# filedir_child  = os.path.join(script_path(),"task")  #解压后放入的目录
	# filedir  = os.path.join(filedir_child,"task_"+time.strftime('%Y%m%d%H%I%S'))  #解压后放入的目录
	# if not os.path.isdir(filedir_child): os.mkdir(filedir_child)  
	# if not os.path.isdir(filedir): os.mkdir(filedir)
	# rar_path = os.path.join(filedir,"task.rar")
	# urllib.urlretrieve(items[0], rar_path)
	# print "download finish!"
	# print "unrar......!"
	# file = rarfile.RarFile(rar_path)  #这里写入的是需要解压的文件，别忘了加路径
	# file.extractall(filedir)  #这里写入的是你想要解压到的文件夹
	# print "unrar finish!"
	# answer_path = Translate(filedir)
	#返回答案结果
	
	#answer = open(answer_path,'r')
	answer = open(os.path.join(script_path(),"task\\task_20171011200841\\data\\ZK133A.txt"),'r')
	#print(answer.readlines().encode('utf8'))
	reader = codecs.getreader('gbk')(answer)
	return reader.read()
	
def get_question(answer_data, task_html, task_url):
	#匹配问题列表
	task_key_word = u'做作业'
	regex_content = re.compile(
            '<div.*?class=\"button_red\".*?<a.*?href=\"(.+?)\".*?class=\"a\_white\".*?>'+task_key_word.encode('gbk')+'</a>',
            re.S)
	items = re.findall(regex_content, task_html.encode('gbk'))
	for item in items:
		#匹配单个问题url
		question_html = getHtmlSource(task_url+item, username, password)
		question_regex = u'【(.*?)】'
		regex_content = re.compile(
            question_regex.encode('gbk'),
            re.S)
		question_num_items = re.findall(regex_content, question_html.encode('gbk'))
		answer = {}
		for question_num_item in question_num_items:
			#匹配问题答案
			answer_regex = u'案】'
			regex_content = re.compile(
				question_num_item+'.*?'+answer_regex.encode('gbk')+'([A-Z])',
				re.S)
			answer_items = re.findall(regex_content, answer_data.encode('gbk'))
			answer[question_num_item] = answer_items
			
		#获取提交答案路径
		regex_content = re.compile(
            '<form.*?id="form1".*?name="form1".*?action="(.*?)"',
            re.S)
		post_question_url_items = re.findall(regex_content, question_html.encode('gbk'))
		post_question_url = task_url+post_question_url_items[0]
		#创建post体
		data = answer
		data['CourseID'] = re.findall(re.compile('<input.*?name=\"CourseID\".*?value=\"(.*?)\"',re.S),question_html)[0]
		data['PMID']     = re.findall(re.compile('<input.*?name=\"PMID\".*?value=\"(.*?)\"',re.S),question_html)[0]
		data['tmpSID']   = re.findall(re.compile('<input.*?name=\'tmpSID\'.*?value=\'(.*?)\'',re.S),question_html.encode('gbk'))[0]
		data['strStandardScore'] = re.findall(re.compile('<input.*?name=\'strStandardScore\'.*?value=\'(.*?)\'',re.S),question_html)[0]
		#post提交答案
		result = getHtmlSource(post_question_url, username, password, data)
		print data
		print result
		return 


def script_path():
	caller_file = inspect.stack()[1][1]         # caller's filename
	return os.path.abspath(os.path.dirname(caller_file))# path

def run():
	html = getHtmlSource(url, username, password)
	items = regex_content = re.compile(
            '<iframe.*?id="iframe".*?src=\"(.+?)\"',
            re.S)
	items = re.findall(regex_content, html)
	task_url = items[0]
	task_url_items = regex_content = re.compile(
            '(.*?\/.*?)[^\/]*\.asp.*?',
            re.S)
	task_url_items = re.findall(regex_content, url)
	task_html = getHtmlSource(task_url_items[0]+task_url, username, password)
	answer_data = downloadTask(task_html)
	get_question(answer_data,task_html,task_url_items[0])
	
if __name__ == '__main__': 
	print run()