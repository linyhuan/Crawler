#!coding=utf-8
import requests
import re
import json
import math
import random
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告
import hashlib
import execjs


class toutiao(object):

    def __init__(self,path,url):
        self.path = path  # CSV保存地址
        self.url=url
        self.s = requests.session()
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
                   'Connection': 'Keep-Alive',

                   }
        self.s.headers.update(headers)
        self.channel=re.search('ch/(.*?)/',url).group(1)

    def closes(self):
        self.s.close()


    def getdata(self):  #获取数据

        req = self.s.get(url=self.url, verify=False)
        #print (self.s.headers)
        #print(req.text)
        headers = {'referer': self.url}
        max_behot_time='0'
        signature='.1.hXgAApDNVcKHe5jmqy.9f4U'
        eas = 'A1E56B6786B47FE'
        ecp = '5B7674A7FF2E9E1'
        self.s.headers.update(headers)
        title = []
        source = []
        source_url = []
        comments_count = []
        tag = []
        chinese_tag = []
        label = []
        abstract = []
        behot_time = []
        nowtime = []
        duration = []
        for i in range(0,30):

            Honey = json.loads(self.get_js())
            # eas = self.getHoney(int(max_behot_time))[0]
            # ecp = self.getHoney(int(max_behot_time))[1]
            eas = Honey['as']
            ecp = Honey['cp']
            signature = Honey['_signature']
            url='https://www.toutiao.com/api/pc/feed/?category={}&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as={}&cp={}&_signature={}'.format(self.channel,max_behot_time,max_behot_time,eas,ecp,signature)
            req=self.s.get(url=url, verify=False)
            time.sleep(random.random() * 2+2)
            print(req.text)
            print(url)
            j=json.loads(req.text)

            for k in range(0, 10):

                now=time.time()
                if j['data'][k]['tag'] != 'ad':
                    title.append(j['data'][k]['title']) ##标题
                    source.append(j['data'][k]['source']) ##作者
                    source_url.append('https://www.toutiao.com/'+j['data'][k]['source_url'])  ##文章链接
                    try:
                        comments_count.append(j['data'][k]['comments_count'])  ###评论
                    except:
                        comments_count.append(0)

                    tag.append(j['data'][k]['tag'])  ###频道名
                    try:
                        chinese_tag.append(j['data'][k]['chinese_tag'])   ##频道中文名
                    except:
                        chinese_tag.append('')
                    try:
                        label.append(j['data'][k]['label'])  ## 标签
                    except:
                        label.append('')
                    try:
                        abstract.append(j['data'][k]['abstract']) ###文章摘要
                    except:
                        abstract.append('')
                    behot=int(j['data'][k]['behot_time'])
                    behot_time.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(behot)))  ####发布时间
                    nowtime.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(now)))  ##抓取时间
                    duration.append(now-behot)   ##发布时长
            time.sleep(2)

            #max_behot_time=str(j['next']['max_behot_time'])
            print('------------'+str(j['next']['max_behot_time']))
            print(title)
            print(source)
            print(source_url)
            print(comments_count)
            print(tag)
            print(chinese_tag)
            print(label)
            print(abstract)
            print(behot_time)
            print(nowtime)
            print(duration)
            data={'title':title,'source':source,'source_url':source_url,'comments_count':comments_count,'tag':tag,
                  'chinese_tag':chinese_tag,'label':label,'abstract':abstract,'behot_time':behot_time,'nowtime':nowtime,'duration':duration,
            }

            df=pd.DataFrame(data=data)
            df.to_csv(self.path+r'\toutiao.csv',encoding='GB18030',index=0)

    def getHoney(self,t):  #####根据JS脚本破解as ,cp
        #t = int(time.time())
        #t=1534389637
        #print(t)
        e =str('%X' % t)
        #print(e)
        m1 = hashlib.md5()
        m1.update(str(t).encode(encoding='utf-8'))
        i = str(m1.hexdigest()).upper()
        #print(i)
        n=i[0:5]
        a=i[-5:]
        s=''
        r=''
        for x in range(0,5):
            s+=n[x]+e[x]
            r+=e[x+3]+a[x]
        eas='A1'+ s+ e[-3:]
        ecp=e[0:3]+r+'E1'
        #print(eas)
        #print(ecp)
        return eas,ecp

    def get_js(self):  ###二牛破解as ,cp,  _signature  参数的代码，然而具体关系不确定，不能连续爬取
        # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
        f = open(r"E:\lyh\data\shichang\toutiao\toutiao-TAC.sign.js", 'r', encoding='UTF-8')
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        ctx = execjs.compile(htmlstr)
        return ctx.call('get_as_cp_signature')

    def ttapi(self):  ####大牛的APP模式
        t2 = int(time.time())-500
        for i in range(10):
            time.sleep(3)

            t=int(time.time())

            params={
            'category':self.channel,
            'refer':'1',   ###???，固定值1
            'count':'20',   ####返回数量，默认为20
            'min_behot_time':t2,          ####上次请求时间的时间戳，例:1491981025
            'last_refresh_sub_entrance_interval':t-10,#####本次请求时间的时间戳，例:1491981165
            'loc_mode':'',
            'loc_time':int(t/1000)*1000,###本地时间
            'latitude':'',###经度
            'longitude':'',###纬度
            'city':'',###当前城市
            'tt_from':'',
            'lac':'',
            'cid':'',
            'cp':'',
            'iid':'2348577934',###某个唯一 id，长度为10
            'device_id':'42433242851',###设备id，长度为11
            'ac':'',
            'channel':'',
            'aid':'',
            'app_name':'',
            'version_code':'',
            'version_name':'',
            'device_platform':'',
            'ab_version':'',
            'ab_client':'',
            'ab_group':'',
            'ab_feature':'',
            'abflag':'3',
            'ssmix':'a',
            'device_type':'',
            'device_brand':'',
            'language':'zh',
            'os_api':'',
            'os_version':'',
            'openudid':'1b8d5bf69dc4a561',####某个唯一id，长度为16
            'manifest_version_code':'',
            'resolution':'',
            'dpi':'',
            'update_version_code':'',
            '_rticket':''

            }
            url='http://is.snssdk.com/api/news/feed/v51/'
            app=self.s.get(url=url,params=params,verify=False)
            print(app.text)
            t2=t-10


if __name__=='__main__':
    path=r'E:\lyh\data\shichang\toutiao'
    url='https://www.toutiao.com/ch/news_tech/'
    t=toutiao(path,url)
    #t.getdata()
    t.ttapi()
    t.closes()


