import requests
import MySQLdb
import random
import json
import time
import _thread as thread
from lxml import etree
#获取数据库连接
def connect_database():
    dbs = MySQLdb.connect(host="0.0.0.0", user="user", passwd="wydiisasdsd##&user", db="AddressPool", charset="utf8")
    return dbs##
#用代理发送get请求，返回内容
def get_html(url,agent):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
    }
    proxies = {
        "http": "http://%s:%s" % (agent[1], agent[3]),
    }
    if agent[2] == "https":
        proxies = {
            "https": "https://%s:%s" % (agent[1], agent[3])
        }
    try:
        reseponse=requests.get(url=url,headers=headers,proxies=proxies,timeout=5)
        if reseponse.status_code==200:
           # print("网页获取成功")
            return reseponse.text
        else:
            print("网页加载错误：",reseponse.status_code)
    except:
        print("网页加载失败,代理超时")
        return None
#从数据库中随机取出一条代理
def get_agent():
    dbs=connect_database()
    cursor=dbs.cursor()
    cursor.execute("select * from address_table2 where type='https'")
    AddressPool = cursor.fetchall()
    dbs.close()
    agent=random.choice(AddressPool)
    #print("代理IP：",agent)
    return agent
#根据xpath筛选页面返回需要数据
def pase_html(text='',xpath='',xobject=None):
    if text!='':
        sous=etree.HTML(text)
    else:
        sous=xobject
    return sous.xpath(xpath)
#根据id查找歌名
def get_songname(songid):
    url='https://music.163.com/song?id='+songid
    xpath='.//meta[@property="og:title"]/@content'
    html=get_html(url,get_agent())
    if(html!=None):
        return pase_html(html,xpath)[0]
#获取歌曲评论总数
def get_comments_total(songid=''):
    url='''https://music.163.com/api/v1/resource/comments/R_SO_4_%s?limit=%d&offset=%d'''%(songid,20,20)
    text=get_html(url,get_agent())
    js_dom=json.loads(text)
    total=js_dom["total"]
    return total
#获取歌曲评论内容
def get_comment(songid='',limit=20,offset=0,username=''):
    url='''https://music.163.com/api/v1/resource/comments/R_SO_4_%s?limit=%d&offset=%d'''%(songid,limit,offset)
    text=get_html(url,get_agent())
    js_dom=json.loads(text)
    comments=js_dom["comments"]
    total=js_dom["total"]
    datas=[]
    for comment in comments:
        data={}
        data["content"]=comment["content"]
        data["time"]=comment["time"]
        user=comment["user"]
        data["userid"]=user["userId"]
        data["username"]=user["nickname"]
        datas.append(data)
    #print(datas)
    pase_username(datas,username)
    return datas
    #http://music.163.com/api/v1/resource/comments/R_SO_4_1442842748?limit=40&offset=105720
def get_Allcomment(songid='',limit=20,username=''):
    # get_comments('28196001',40,40)
    total = get_comments_total(songid)
    songname = get_songname(songid)
    print("歌名:"+songname+"  搜索昵称:"+username+"  歌曲总评论数:"+str(total))
    print("开始搜索：")
    startime=time.time()
    if(total<=2000):
        for i in range(0, total, limit):
            get_comment(songid, limit, i,username)
    else:
        for i in range(0, 1000, limit):
            get_comment(songid, limit, i,username)
        for i in range(total - 1000, total + limit, limit):
            get_comment(songid, limit, i,username)
    stoptime=time.time()
    print("搜索结束,花费"+str(int(stoptime-startime))+"秒")
def pase_username(datas,username=''):
    #print("进入解析：")
    for data in datas:
        if data["username"]==username:
            timeArray=time.localtime(float(data["time"]/1000))
            otherStyleTime=time.strftime("%Y-%m-%d %H:%M:%S",timeArray)
            print(data["username"]+":"+data["content"]+"\t时间:"+str(otherStyleTime))
def Playlist_songid(id,username):
    url="https://music.163.com/playlist?id="+id
    xpath='.//ul[@class="f-hide"]/li'
    html=get_html(url,get_agent())
    PlaylistName=pase_html(text=html,xpath='.//meta[@property="og:title"]/@content')[0]
    lis=pase_html(text=html,xpath=xpath)
    songids=[]
    for li in lis:
        href=pase_html(xpath='./a/@href',xobject=li)[0]
        id=href.split('=')[1]
        songids.append(id)
    print("               歌单名:",PlaylistName)
    for songid in songids:
        get_Allcomment(songid=songid,limit=100,username=username)
    pass
if __name__=="__main__":
    N='0'
    while(1):
        N=str(input("歌单搜索评论||单个歌曲搜索评论（1,2）:"))
        if N=='1':
            songid=str(input("输入歌单ID:"))
            name=str(input("输入搜索昵称:"))
            Playlist_songid(songid,name)
        elif N=='2':
            songid = str(input("输入歌曲ID:"))
            name = str(input("输入搜索昵称:"))
            get_Allcomment(songid=songid,limit=100,username=name)
        else:
            print("输入不符合要求！！")
    #Playlist_songid('4988462925')
