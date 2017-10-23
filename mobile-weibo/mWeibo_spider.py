import re
import sys
import os
import string
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from threading import Thread,Lock
import requests
from lxml import etree
"""
1.获取图片不能获取原图
2.如果图片有组图，只能获取第一张
"""
class WeiboUser(object):
    def __init__(self,uid):
        self.uid = uid
        self.pageNum = 0
        self.item_count = 1
        self.image_count = 1
        self.textResult = ""
        self.cookie = {"Cookie":""}
        #self.mutex = Lock()
    def initialize(self):
        #https://m.weibo.cn 和PC版一样会进行重定向
        #filter=1 : 原创微博
        url = "https://weibo.cn/u/%s?filter=1&page=1"%self.uid
        cookieFile = open("./cookie.txt","r")
        self.cookie["Cookie"] = str(cookieFile.read())
        #request.get()
        #没有cookie不能访问
        try:
            html = requests.get(url,cookies=self.cookie).content
            print(html.decode("utf-8"))
            seletor = etree.HTML(html)
            self.pageNum = (int)(seletor.xpath("//input[@name='mp']")[0].attrib["value"])
        except Exception as e:
            print("------------initialize error----------")
            print(e)

    
    def getText(self,lxml):
        selector = etree.HTML(lxml)
        content = selector.xpath("//span[@class='ctt']")
        
        for item in content:
            text = item.xpath("string(.)")
            if self.item_count >= 3:
                text = "%d "%(self.item_count-2) + text
                print("----------获取第%d条微博----------"%(self.item_count-2))
            text += "\n\n"
            self.textResult += text
            self.item_count += 1
        try:
            f = open("./weiboTxt%s"%self.uid,"w")
            f.write(self.textResult)
        except IOError:
            print("IO ERROR")
        finally:
            f.close()

    def getImage(self,lxml):
        bsObj = BeautifulSoup(lxml,"lxml")
        urllist = bsObj.findAll("a")
        folder = "./uid"+uid+"Weibo"
        
        if not os.path.exists(folder):
            os.mkdir(folder)

        for item in urllist:
            img = item.find("img")
            if img != None and "src" in img.attrs:
                urlretrieve(img["src"],"%s/%d.jpg"%(folder,self.image_count))
                print("----------获取第%d张图片----------"%self.image_count)
                self.image_count += 1

    def startScripy(self):
        self.initialize()
        #对每一页微博进行访问
        for page in range(1,self.pageNum+1):
            #获取lxml页面
            url = "https://weibo.cn/u/%s?filter=1&page=%d"%(self.uid,page)
            lxml = requests.get(url,cookies=self.cookie).content
            self.getText(lxml)
            self.getImage(lxml)
            #微博原创文字获取
            #textThd = Thread(target=self.getText,args=(lxml,))
            #textThd.start()
            #textThd.join()
            #获取原创图片
            #imgThd = Thread(target=self.getImage,args=(lxml,))
            #imgThd.start()
    
if __name__ == "__main__":
    uid = input(">输入用户id：")
    spider = WeiboUser(uid)
    spider.startScripy()