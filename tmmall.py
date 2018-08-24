#!coding=utf-8
import requests
import re
import random
import time
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告

class tm(object):####手机端

    def __init__(self,path):  ###保存数据路径
        self.path=path

    def goodsid(self,url):  ###通过店铺URL获取店铺所有ID
        shopname = re.search('https://(.*?).tmall', url).group(1)
        searchurl = 'https://{}.m.tmall.com/shop/shop_auction_search.do?spm=a1z60.7754813.0.0.301755f0pZ1GjU&sort=defaul'.format(
            shopname)
        s=requests.session()
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) FxiOS/10.6b8836 Mobile/14G60 Safari/603.3.8',
                   'Referer':'https://{}.m.tmall.com/shop/shop_auction_search.htm?spm=a1z60.7754813.0.0.301755f0pZ1GjU&sort=default'.format(shopname)
                   }
        s.headers.update(headers)
        page1=s.get(url=searchurl,verify=False).text
        print(page1)
        js=json.loads(page1)
        total_page=int(js['total_page'])
        shop_id=js['shop_id']
        shop_title = js['shop_title']
        shop_id_list = []
        shop_title_list = []

        item_id=re.findall('"item_id":(.*?),"',page1)
        title=re.findall('"title":"(.*?)","',page1)
        sold=re.findall('"sold":"(.*?)","',page1)
        totalSoldQuantity=re.findall('"totalSoldQuantity":(.*?),"',page1)
        skuurl=re.findall('"url":"(.*?)","',page1)
        price=re.findall('"price":"(.*?)","',page1)
        item_id_l=len(item_id)
        shop_id_list.append(shop_id)
        shop_id_list.extend(shop_id_list*(int(item_id_l)-1))
        shop_title_list.append(shop_title)
        shop_title_list.extend(shop_title_list*(int(item_id_l)-1))
        # print(js)
        # print(len(shop_id_list))
        # print(len(shop_title_list))
        # print(len(item_id))
        # print(len(title))
        # print(len(sold))
        # print(len(totalSoldQuantity))
        # print(len(skuurl))
        # print(len(price))


        data = {'shop_id': shop_id_list,'shop_title': shop_title_list,'item_id': item_id, 'title': title, 'sold':sold, 'totalSoldQuantity':totalSoldQuantity, 'skuurl':skuurl, 'price':price}
        df = pd.DataFrame(data=data)
        #print(df)
        savepath=self.path + r'\tmgoodsid{}.csv'.format(shopname)
        print(savepath)
        df.to_csv(savepath, mode='a', index=False, encoding="GB18030")
        time.sleep(random.random() * 2)
        if total_page!=1:

            for i in range(2,total_page+1):
                time.sleep(random.random() * 2)
                htmlurl=searchurl+'&p={}'.format(i)
                html=s.get(url=htmlurl,verify=False).text
                shop_id_list = []
                shop_title_list = []
                print(html)
                item_id = re.findall('"item_id":(.*?),"',html)
                title = re.findall('"title":"(.*?)","', html)
                sold = re.findall('"sold":"(.*?)","', html)
                totalSoldQuantity = re.findall('"totalSoldQuantity":(.*?),"', html)
                skuurl = re.findall('"url":"(.*?)","', html)
                price = re.findall('"price":"(.*?)","',html)
                item_id_l = len(item_id)
                shop_id_list.append(shop_id)
                shop_id_list.extend(shop_id_list * (int(item_id_l) - 1))
                shop_title_list.append(shop_title)
                shop_title_list.extend(shop_title_list * (int(item_id_l) - 1))

                data = {'shop_id': shop_id_list, 'shop_title': shop_title_list, 'item_id': item_id, 'title': title,
                        'sold': sold, 'totalSoldQuantity': totalSoldQuantity, 'skuurl': skuurl, 'price': price}
                df = pd.DataFrame(data=data)
                df.to_csv(self.path + r'\tmgoodsid{}.csv'.format(shopname),mode='a', index=False,header=0 ,encoding="GB18030")
        df1 = pd.read_csv(self.path + r'\tmgoodsid{}.csv'.format(shopname), encoding='GB18030')
        s.close()
        return df1
    def getiddata(self,id):   ###获取ID数据
        time.sleep(random.random() * 1 + 1)
        s = requests.session()
        t=int(time.time()*1000)
        url='https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/' \
            '?jsv=2.4.8&appKey=12574478&t={}' \
            '&sign=7c9e1dedaa295fdb175d22c99746493b&api=mtop.taobao.detail.getdetail' \
            '&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&' \
            'data=%7B%22itemNumId%22%3A%22{}%22%7D'.format(t,id)

        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) FxiOS/10.6b8836 Mobile/14G60 Safari/603.3.8',
                   'Referer': 'https://detail.m.tmall.com/item.htm?spm=a220m.6910245.0.0.55b17434eiwv4f&id={}'.format(id)
                   }
        print(url)
        s.headers.update(headers)
        html = s.get(url=url, verify=False).text
        html=html.replace('\\','')
        time.sleep(0.5)
        info=re.search('skuBase":(.*?),"skuCore',html)
        if info!=None:
            skuBase=re.search('skuBase":(.*?),"skuCore',html).group(1) ##SKU+颜色
            skuId = re.findall('"skuId":"(.*?)","', skuBase)
            propPath=re.findall('"propPath":"(.*?)"}',skuBase)
            skuBase=json.loads(skuBase)
            prop_list=[]
            for i in propPath:
                prop = ''
                prop1=i.split(';')
                for j in prop1:
                    prop2=j.split(':')
                    for pid in skuBase['props']:
                        if pid['pid']==prop2[0]:
                            #prop=prop+pid['name']
                            for vid in pid['values']:
                                if vid['vid']==prop2[1]:
                                    prop=prop+vid['name']
                prop_list.append(str(prop))
            sku2info = re.search('"sku2info":(.*?)},"s', html).group(1)  ##价格
            sku2info = json.loads(sku2info)
            price = []
            for i in skuId:
                p = sku2info[str(i)]['price']['priceText']
                price.append(p)
        else:
            skuId=[' ']
            prop_list=[' ']
            price=[' ']




        data = {'skuid': skuId, 'prop': prop_list,'price':price}
        df = pd.DataFrame(data=data)

        return df

    def iddata(self,id_df):
        df_l=id_df.iloc[:,0].size
        df=pd.DataFrame()
        df.loc[0, "shop_id"] = ''
        df.loc[:, "shop_title"] = ''
        df.loc[:, "item_id"] = ''
        df.loc[:, "title"] = ''
        df.loc[:, "sold"] = ''
        df.loc[:, "totalSoldQuantity"] = ''
        df.loc[:, "skuurl"] = ''
        df.loc[:, "price"] = ''
        df.loc[:, "skuid"] = ''
        df.loc[:, "prop"] = ''
        df.loc[:, "skuprice"] = ''
        shopid=id_df['shop_id'][1]
        y=0
        for i in range(0,df_l):
            time.sleep(random.random() * 2.56)
            pid=id_df['item_id'][i]
            data=self.getiddata(pid)
            data_l=data.iloc[:,0].size
            for j in range(0,data_l):
                df.at[y, "shop_id"] = id_df['shop_id'][i]
                df.at[y, "shop_title"] = id_df['shop_title'][i]
                df.at[y, "item_id"] = id_df['item_id'][i]
                df.at[y, "title"] = id_df['title'][i]
                df.at[y, "sold"] = id_df['sold'][i]
                df.at[y, "totalSoldQuantity"] = id_df['totalSoldQuantity'][i]
                df.at[y, "skuurl"] = id_df['skuurl'][i]
                df.at[y, "price"] = id_df['price'][i]
                df.at[y, "skuid"] = data['skuid'][j]
                df.at[y, "prop"] = data['prop'][j]
                df.at[y, "skuprice"] = data['price'][j]
                y +=1
            df.to_csv(self.path + r'\tm{}.csv'.format(shopid), index=False, encoding="GB18030")
        return df


    def urlitem(self,url,*args):   ##通过目录获取  只适合部分
        s = requests.session()
        headers = {'Accept': '*/*',
                   'Accept-Language': 'zh-CN',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36'
                   }

        s.headers.update(headers)
        itemhtml = s.get(url=url, verify=False).text
        #print(itemhtml)
        shopid = re.search('class="J_TModule"(.*?)"搜索列表"', itemhtml).group(1)
        shopid=re.search('data-widgetid="(.*?)"  id',shopid).group(1)
        #print(shopid)
        id=re.search('category-(.*?).htm',url).group(1)
        nm=re.search('https://(.*?).tmall.com/',url).group(1)
        t=int(time.time()*1000)
        pageurl='https://{}.tmall.com/i/asynSearch.htm?_ksTS={}_888&callback=jsonp289&mid=w-{}-0&wid={}&path=/category-{}.htm'.format(nm,t,shopid,shopid,id)

        print(pageurl)
        time.sleep(random.random() * 1 + 1)
        html = s.get(url=pageurl, verify=False).text
        html = html.replace('\\', '')
        html=re.sub('\n','',html)
        page=re.search('ui-page-s-len">1/(.*?)</b>',html).group(1)
        print(page)
        nm_list=[]
        idurl_list=[]
        price_list=[]
        sale_list=[]


        for p in range(1,int(page)+1):
            time.sleep(random.random())
            pageurl = 'https://{}.tmall.com/i/asynSearch.htm?_ksTS={}_888&callback=jsonp289&mid=w-{}-0&wid={}&path=/category-{}.htm'.format(
                nm, t, shopid, shopid, id)
            html = s.get(url=pageurl, verify=False).text
            html = html.replace('\\', '')
            html = re.sub('\n', '', html)
            print(html)
            nm=re.findall('<img alt="(.*?)" data',html)[:-8]
            print(nm)
            id=re.findall('<a href="//detail.(.*?)&rn',html)
            idurl=[]
            for i in id:
                idurl.append('https://detail.'+i)
            price=re.findall('class="c-price">(.*?) ',html)[:-8]
            sale=re.findall('sale-num">(.*?)</span>',html)[:-8]
            nm_list.extend(nm)
            idurl_list.extend(idurl)
            price_list.extend(price)
            sale_list.extend(sale)
            print(len(nm_list))
            print(len(idurl_list))
            print(len(price_list))
            print(len(sale_list))

            data={'nm':nm_list,'idurl':idurl_list,'price':price_list,'sale':sale_list}
            df=pd.DataFrame(data)
            l=len(args)
            for j in range(0,l):
                df.loc[:, "col"+str(j)] = args[j]
            print(df)
        s.close()
        return df
        # 例子：
        # tm = tm()
        # url = 'https://shoushanggeshi.tmall.com/category-1310604910.htm'
        # # url = 'https://shoushanggeshi.tmall.com/category-674950482.htm'
        # tm.urlitem(url, '电脑', 'cpu')







if __name__=='__main__':
    path=r'E:\lyh\data\mallprice\tm\0818'
    tm=tm(path)

#     r=[
# 'https://tiansebg.tmall.com',
# 'https://tiansety.tmall.com',
# 'https://tiansegz.tmall.com',
# 'https://tiansetc.tmall.com',
# 'https://tianseasd.tmall.com',
# 'https://tiansemanyu.tmall.com',
# 'https://tianseyj.tmall.com/'
#
#     ]

    df=tm.goodsid('https://tiansegz.tmall.com')
    tm.iddata(df)
    print('-------------')
    df = tm.goodsid('https://tiansetc.tmall.com')
    tm.iddata(df)
    print('-------------')
    df = tm.goodsid('https://tianseasd.tmall.com')
    tm.iddata(df)
    print('-------------')
    df = tm.goodsid('https://tiansemanyu.tmall.com')
    tm.iddata(df)
    print('-------------')
    df = tm.goodsid('https://tianseyj.tmall.com')
    tm.iddata(df)
    print('-------------')


