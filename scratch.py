import requests
from bs4 import BeautifulSoup
import codecs
import sys
import html2text
from data import *
from imp import reload
import re
import os
reload(sys)

def getArticleList():
    title_list = []
    href_list = []
    for page in range(1,4):
        url = 'https://blog.csdn.net/u011021773/article/list/%d'%page
        strhtml = requests.get(url)
        content = strhtml.content.decode('utf-8')
        soup = BeautifulSoup(content,'lxml') 
        article_list = soup.findAll(name="div", attrs={"class" :"article-list"})
        h4 = article_list[0].findAll(name="h4")
        for a in h4:
            tag = a.findAll(name="span")[0].get_text()
            title = a.get_text().replace(tag, '')
            title = title.replace('  ','') 
            title = title.replace('\n','') 
            title = title.replace('<','《') 
            title = title.replace('>','》') 
            title = title.replace(':','-') 
            title = title.replace(' ','-') 

            print(title)
            title_list.append(title)
            href_list.append(a.find(name="a").get("href"))
    return title_list, href_list

def getHtml(url):
    strhtml = requests.get(url)
    content = strhtml.content.decode('utf-8')
    soup = BeautifulSoup(content,'lxml') 
    article = soup.find(name="div", attrs={"id" :"content_views"})
    return str(article)

def download_img(img_url, path):
    print (img_url)
    r = requests.get(img_url, stream=True)
    print(r.status_code) # 返回状态码
    if r.status_code == 200:
        open(path, 'wb').write(r.content) # 将内容写入图片
        print("done")
    del r

def deal_with_img(mdTxt, title, root_url):
    result = mdTxt
    tempTxt = mdTxt
    count = 0
    posList = []
    pos = 0
    while True:
        pattern=re.compile(r"!\[(.*?)\]\((.*?)\)")
        fullid = pattern.search(tempTxt)
        if fullid is None:
            break
        fullstr = tempTxt[fullid.start(): fullid.end()]
        pattern=re.compile(r"\((.*?)\)")
        urlid = pattern.search(fullstr)
        if urlid is None:
            break
        posList.append([pos + fullid.start() + urlid.start() + 1,
            pos + fullid.start() + urlid.end() - 1]) #这里+1和-1是去掉前后的小括号
        pos += fullid.start() + urlid.end()
        if pos >= len(mdTxt):
            break
        tempTxt = mdTxt[pos:]

    # path = os.path.join("CSDN", title)
    # if not os.path.exists(path):
        # os.mkdir(path)
    
    path = title
    for i in range(len(posList)):
        pos = posList[-i-1]
        url = mdTxt[pos[0]:pos[1]]
        if url[:4] != 'http':
            url = 'http://i.imgur.com' + url
        try:
            r = requests.get(url)
        except Exception as e:
            print(e)
            print(url)
            print(url[:4])
            continue
        id = url.find('?')
        if id > 0 :
            url = url[:id]
        img_path = os.path.join('G:\\blog\\keefeWu.github.io\\source\\_posts', path, '%d%s'%(len(posList) - i, os.path.splitext(url)[1]))
        with open(img_path, 'wb') as f:
            f.write(r.content)
        result = result[:pos[0]] + '%d%s'%(len(posList) - i, os.path.splitext(url)[1]) + result[pos[1]:]              
    return result
    

def main():
    title_list, href_list = getArticleList()
    html_data_list = []
    for i in range(len(href_list)):
        html_data = getHtml(href_list[i])
        html_data_list.append(html_data)
    for i in range(len(href_list)):
        html_data = html_data_list[i]
        mdTxt = html2text.html2text(html_data)
        print(title_list[i])
        cmd = 'G: && \
                cd G:\\blog\\keefeWu.github.io &&\
                hexo new %s'%title_list[i]
        print(cmd)
        os.system(cmd)
        mdTxt = deal_with_img(mdTxt, title_list[i], href_list[i])
        file = open('G:/blog/keefeWu.github.io/source/_posts/%s.md'%title_list[i], 'a', encoding="utf-8")
        file.write(mdTxt)
        file.close()
# main()