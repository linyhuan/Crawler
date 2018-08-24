#!coding=utf-8
import requests
import re
import math
import random
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告


class suning(object):

    def __init__(self,path):
        self.path=path #CSV保存地址
        self.s=requests.session()
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36'
                   }
        self.s.headers.update(headers)

    def closes(self):
        self.s.close()

    def get_shopid(self,url):  #获取店铺ID号


        page = self.s.get(url=url, verify=False).text
        #print(page)
        shopid=re.search('@id": "(.*?)://shop.suning.com/(.*?)/index.html"',page).group(2)
        shopnm=re.search('<title>(.*?)</title>',page).group(1)
        if len(shopid) < 10:
            l = 10 - len(shopid)
            shopid = '0' * l+shopid

        return shopid,shopnm

    def goodid(self,url):   #获取店铺商品SPU

        shop=self.get_shopid(url)
        shopid=shop[0]
        shopnm=shop[1]
        url='https://csearch.suning.com/emall/cshop/queryByKeyword.do?vendor_Id={}&keyword=&start=0&rows=48&sortField=&cf=price:&pcode=&callback=jsonpQueryByKeyword'.format(shopid)
        page = self.s.get(url=url, verify=False).text
        time.sleep(random.random())
        total=re.search('"totalSize":(.*?),',page).group(1)
        p=math.ceil(int(total)/48)
        df = pd.DataFrame()
        df.loc[0, "nm"] = ''
        df.loc[:, "url"] = ''
        df.loc[:, "spu"] = ''
        df.loc[:, "subColors"] = ''
        df.loc[:, "price1"] = ''
        df.loc[:, "countOfarticle"] = ''
        df.loc[:, "praiseRate"] = ''
        df.loc[:, "firstShelfTime"] = ''
        df.loc[:, "inventory"] = ''
        df.to_csv(self.path + r'\sngoodid.csv', index=False, encoding="GB18030")
        y=0

        for i in range(0,p):
            start = i*48
            url = 'https://csearch.suning.com/emall/cshop/queryByKeyword.do?vendor_Id={}&keyword=&start={}&rows=48&sortField=&cf=price:&pcode=&callback=jsonpQueryByKeyword'.format(
                shopid,start)
            html=self.s.get(url=url, verify=False).text
            time.sleep(random.random())

            nm=re.findall('"catentdesc":"(.*?)"}',html)
            url=re.findall('"commidityUrl":"(.*?)",',html)
            price=re.findall('"price":"(.*?)",',html)
            countOfarticle=re.findall('"countOfarticle":"(.*?)",',html)
            praiseRate=re.findall('"praiseRate":(.*?),',html)
            firstShelfTime=re.findall('"firstShelfTime":"(.*?)",',html)
            inventory=re.findall('"inventory":"(.*?)",',html)
            subColors=re.findall('"subColors":(.*?),"',html)
            nm_l=len(nm)
            #print(nm)
            #print(subColors)
            for j in range(0,nm_l):
                if subColors[j]=='""':
                    df.at[y, "nm"] = nm[j]
                    df.at[y, "url"] = url[j]
                    df.at[y, "price1"] = price[j]
                    df.at[y, "countOfarticle"] = countOfarticle[j]
                    df.at[y, "praiseRate"] = praiseRate[j]
                    df.at[y, "firstShelfTime"] = firstShelfTime[j]
                    df.at[y, "inventory"] = inventory[j]
                    df.at[y, "spu"] =re.search('\d/(.*?).html',url[j]).group(1).strip()
                    df.at[y, "subColors"] = ''
                    df.to_csv(self.path + r'\sngoodid.csv', index=False, encoding="GB18030")
                    y+=1
                else:
                    s_sub=subColors[j].split(',')
                    print(s_sub)
                    for k in range(0,len(s_sub)):

                        df.at[y, "spu"] = s_sub[k].split('|')[0].replace('"','').strip()
                        df.at[y, "subColors"] =s_sub[k].split('|')[2]
                        df.at[y, "nm"] = nm[j]
                        df.at[y, "url"] = url[j]
                        df.at[y, "price1"] = price[j]
                        df.at[y, "countOfarticle"] = countOfarticle[j]
                        df.at[y, "praiseRate"] = praiseRate[j]
                        df.at[y, "firstShelfTime"] = firstShelfTime[j]
                        df.at[y, "inventory"] = inventory[j]
                        y+=1
                        df.loc[:, "shopnm"] = shopnm
                        df.to_csv(self.path + r'\sngoodid.csv',index=False, encoding="GB18030")
                        #print(str(df['spu'][y]))
        print(df)
        return df

    def spudata(self,df):
        df_l=len(df['nm'])
        x=math.ceil(df_l/20)
        price_list=[]
        for i in range(0,x):
            spus=''
            shopids=''
            if i ==(x-1):
                ii=df_l-i*20
            else:
                ii=20
            for j in range(0,ii):
                y=i*20+j
                spu=str(df['spu'][y])
                #print(y)
                spu='0'*(18-len(spu))+spu
                if spus=='':
                    spus += spu
                else:
                    spus+=','+spu
                shop=re.search('com/(.*?)/',df['url'][y]).group(1)
                if shopids=='':
                    shopids += shop
                else:
                    shopids+=','+shop
            #print(len(spus))
            url=r'https://icps.suning.com/icps-web/getVarnishAllPrice014/{}_020_0200101_{}_1_getClusterPrice.vhtm?callback=getClusterPrice'.format(spus,shopids)
            html=self.s.get(url=url, verify=False).text
            time.sleep(random.random())
            price=re.findall('"price":"(.*?)",',html)
            print(price)
            price_list.extend(price)
            #print(len(price))
        df.loc[:, "price"] = price_list
        df.to_csv(self.path + r'\spudata.csv', index=False, encoding="GB18030")
        return df


if __name__=='__main__':
    path=r'E:\lyh\data\mallprice\sn\0814'
    sn=suning(path=path)
    url='https://phoenix.suning.com'
    df=sn.goodid(url)
    #df=pd.read_csv(path+'\sngoodid.csv',encoding="GB18030")
    sn.spudata(df)
    sn.closes()
