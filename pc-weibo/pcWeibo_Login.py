import re
import rsa
import json
import base64
import urllib
import binascii
import http
from bs4 import BeautifulSoup
from http import cookiejar
from urllib import error,request,parse

class Launcher(object):
	def __init__(self,userName,passWord):
		self.userName = userName
		self.passWord = passWord


	def get_encrypted_name(self):
		#模拟加密用户名
		userName_urlLike = request.quote(self.userName)
		userName_encrypted = base64.b64encode(bytes(userName_urlLike,"utf-8"))
		#print(userName_encrypted.decode("utf-8"))
		return userName_encrypted.decode("utf-8")


	def get_prelogin_args(self):
		#预登陆过程，返回response消息
		#nonce，servertime，pub_key
		#https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=MTg1NTY0MTU1JTQwcXEuY29t&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1505893694489
		json_pattern = re.compile("\((.*)\)")
		preprelogin_url = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="+self.get_encrypted_name()+"&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1507188938958"
		try:

			response = request.urlopen(preprelogin_url)
			data = json_pattern.search(response.read().decode("utf-8")).group(1)
			json_data = json.loads(data)
			
			return json_data
		except urllib.error.URLError as e:
			print(e)
			return None	

	def get_encrypted_pw(self,data):
		rsa_e = 65537 #0x10001
		pw_string = str(data["servertime"]) + "\t" + str(data["nonce"]) + "\n" +str(self.passWord)
		key = rsa.PublicKey(int(data["pubkey"],16),rsa_e)

		pw_encypted = rsa.encrypt(pw_string.encode("utf-8"),key)
		pw = binascii.b2a_hex(pw_encypted)
		self.passWord = ""
		return pw

	#保存登录过程的cookie
	def enableCookies(self):
		#build cookies container
		cookie_container = cookiejar.CookieJar()
		#cookies controler
		cookie_support = request.HTTPCookieProcessor(cookie_container)
		#创建一个opener，设置一个handler用于处理http的url打开
		opener = request.build_opener(cookie_support,request.HTTPHandler)
		#安装opener，以后调用urlopen()时会使用安装过的opener对象
		request.install_opener(opener)


	def bulid_post_data(self,raw):
		#表单在
		#qrcode_flag:false
		post_data = {
			"entry":"weibo",
			"gateway":"1",
			"from":"",
			"savestate":"7",
			"useticket":"1",
			"qrcode_flag":"false",
			"pagerefer":"http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
			"vsnf":"1",
			"su":self.get_encrypted_name(),
			"service":"miniblog",
			"servertime":raw['servertime'],
			"nonce":raw["nonce"],
			"pwencode":"rsa2",
			"rsakv":raw["rsakv"],
			"sp":self.get_encrypted_pw(raw),
			"sr":"1920*1080",
			"encoding":"UTF-8",
			"prelt":"65",
			"url":"http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
			"returntype":"META"
		}
		data = parse.urlencode(post_data).encode("utf-8")
		return data

	def login(self):
		url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
		#self.enableCookies()
		data = self.get_prelogin_args()
		post_data = self.bulid_post_data(data)
		headers = {
			"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
		}
		try:
			#提交form表单给预登陆页面
			request_prelogin = request.Request(url=url,data=post_data,headers=headers)
			response_prelogin = request.urlopen(request_prelogin)
			html_prelogin = response_prelogin.read().decode("GBK")
		except urllib.error.URLError as e:
			print(e)


		pattern = re.compile('location\.replace\("(.*)"\)')
		pattern2 = re.compile("\((.*)\)")
		try:
			#第一次重定向url提取
			prelogin_url = pattern.search(html_prelogin).group(1)
			print(prelogin_url)
			request_login = request.Request(prelogin_url)
			response_login = request.urlopen(request_login)

			html_login = response_login.read().decode("GBK")
			
			#第二次重定向url提取
			data = pattern2.search(html_login).group(1)
			#print(data)
			json_group = json.loads(data)
			#print(json_group)
			login_url = "www.weibo.com/" + json_group["userinfo"]["userdomain"]

			return login_url
		except Exception as e:
			print("1----------------")
			print(e)
if __name__ == "__main__":
	user = Launcher("185564155@qq.com","PIS1996.")
	user.enableCookies()
	url = user.login()
