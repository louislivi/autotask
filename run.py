#!/usr/bin/python
#-*-coding:utf-8-*-

import urllib2
import urllib
import zipfile
import re
import time
import os
from unrar import rarfile
import inspect, os
from docx import Document

#登录的用户名和密码
username = "cqliwei321"
password = "liwei123"
url="http://learning.cmr.com.cn/student/acourse/HomeworkCenter/index.asp?courseid=zk133a"

def getHtmlSource(url, username, password):
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
        #urllib2.urlopen 使用上面的opener.  
        ret = urllib2.urlopen(url)

        return ret.read()
    except urllib2.HTTPError, e:
        if e.code == 401:
           return "authorization failed"
        else:
            raise e
    except:
        return None
		
def downloadTask(html):
	regex_content = re.compile(
            '<div.*?class="button_blue2".*?href=\"(.+?)\"',
            re.S)
	items = re.findall(regex_content, html)
	print "downloading with urllib"
	filedir  = os.path.join(script_path(),"task_"+time.strftime('%Y%m%d%H%I%S'))  #解压后放入的目录
	if os.path.isdir(filedir):
		pass
	else:
		os.mkdir(filedir)  
	rar_path = os.path.join(filedir,"task.rar")
	urllib.urlretrieve(items[0], rar_path)
	print "download finish!"
	print "unrar......!"
	file = rarfile.RarFile(rar_path)  #这里写入的是需要解压的文件，别忘了加路径
	file.extractall(filedir)  #这里写入的是你想要解压到的文件夹
	print "unrar finish!"
	filelist=os.listdir(filedir)
	for i in filelist:
		fullfile = os.path.join(filedir,i)
		if not os.path.isdir(fullfile):
			if ".doc" in i:    #1.txt为你所查找的文件名
				document = Document(os.path.join(script_path(),"task_20171011010142\ZK133A.docx"))
				for p in document.paragraphs:
					print p.text
				print docText
				print fullfile
			else:
				pass
	
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
	return downloadTask(task_html)

print run()