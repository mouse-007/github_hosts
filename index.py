from requests import get,post
from html.parser import HTMLParser
import re
import os

baseUrl = 'https://www.ipaddress.com/ip-lookup'
githubLinks={
    'github.global.ssl.fastly.net': '',
    # 'github.com': '',
    'github.githubassets.com': '',
    'collector.githubapp.com': '',
    'avatars.githubusercontent.com': ''
}

class GetIp(HTMLParser):

    '''解析html文档获取ip'''
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.text = None
        self.flag = 'start'
        self.ips = []  

    def handle_starttag(self, tag, attrs):

        '''标签开始'''

        if tag == 'h1' and self.flag == 'start':
            self.flag = "pending"

        if tag == 'input' and attrs.__contains__(('name', "host")) and attrs.__contains__(("type", "radio")):
            for (k, v) in attrs:
                if k == 'value':
                    self.ips.append(v)

    def handle_data(self, data):

        '''读取内容容'''

        if self.flag == 'pending' and self.text == None:
            # print("data==========>", data)
            self.flag = 'end'
            regText = re.search(r'\d+\.\d+\.\d+\.\d+', data)
            if regText != None:
                self.text = regText.group()

    def print_data(self):

        ''' 输出ip '''

        # print("print", self.text, self.ips)
        if self.text != None:
            # print("text",self.text)
            return self.text
        else:
            # print("ips",self.ips)
            return self.ips[0]      

    def reset(self):
        ''' 重置HTMLParser实例 '''
        self.text = None
        self.flag = 'start'
        self.ips = []
        HTMLParser.reset(self)
        

class writeHostsFile():
    ''' 操作hosts文件 '''
    def __init__(self):
        self.file_read = None
        self.path = self.getHostFilePath()
        self.content = []
    
    def getHostFilePath(self):
        ''' 获取hosts文件路径'''
        winDir = [os.getenv("windir"), "System32", "drivers", "etc", "hosts"]
        return "\\".join(winDir)
    
    def open(self):
        ''' 打开hosts文件'''
        self.file_read = open(self.path, mode='r+')
        self.content = self.file_read.readlines()

    def replice(self, str_text, r_str):
        '''替换hosts内容'''
        for index, item in enumerate(self.content):
            if item.startswith("#") == False and item.find(str_text) != -1:
                print("原始字符串", item)
                print("替换字符串", r_str)
                self.content[index] = r_str + '\n'
                return

        print("新增：%s" % (r_str))
        self.content.append(r_str + '\n')

    
    def resriteFile(self):
        self.file_read.seek(0, 0)
        self.file_read.truncate(0)
        self.file_read.writelines(self.content)

    def end(self):
        self.resriteFile()
        self.file_read.close()
        # print(self.content)


def flush_dns():
    os.system("ipconfig /flushdns")

def sendResquest(url):
    data={ "host": url }
    baseUrl = 'https://www.ipaddress.com/ip-lookup'
    headers={
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
    }
    return post(baseUrl, data=data, headers=headers).text

def sendAll(data):

    host_file = writeHostsFile()
    host_file.open()
    print("<======== 开始 =========>")
    for key in data.keys():
        print("处理域名：%s" % (key))
        parser = GetIp()
        resText = sendResquest(key)
        parser.feed(resText)
        ip = parser.print_data()
        parser.reset()
        r_str = "%s   %s" % (ip, key)
        host_file.replice(key, r_str)

    print("<======== 写入 =========>")
    host_file.end()
    print("<======== 刷新dns =========>")
    flush_dns()


sendAll(githubLinks)
input("按任意键关闭")

