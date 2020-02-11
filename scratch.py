import requests
from bs4 import BeautifulSoup
import codecs
import sys
import html2text
from data import *
from imp import reload
import re
import os
from tqdm import tqdm
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

def deal_with_img(html_data, title, root_url):
    result = html_data
    tempTxt = html_data
    count = 0
    posList = []
    pos = 0
    soup = BeautifulSoup(html_data,'lxml') 
    allImg = soup.findAll("img")
    path = title
    for i in range(len(allImg)):
        url = allImg[i]['src']
        try:
            r = requests.get(url)
        except Exception as e:
            print(e)
            print(url)
            continue
        ori_url = url
        id = url.find('?')
        if id > 0 :
            url = url[:id]
        suffix = os.path.splitext(url)[1]
        if suffix == '':
            suffix = '.png'
        img_name = '%d%s'%(i, suffix)
        img_path = os.path.join('G:\\blog\\keefeWu.github.io\\source\\_posts', path, img_name)
        with open(img_path, 'wb') as f:
            f.write(r.content)
        result = result.replace(ori_url, img_name)
    return result
    

def main():
    title_list, href_list = getArticleList()
    html_data_list = []
    for i in tqdm(range(len(href_list))):
        html_data = getHtml(href_list[i])
        html_data_list.append(html_data)
    for i in tqdm(range(len(href_list))):
        html_data = html_data_list[i]
        print(title_list[i])
        cmd = 'G: && \
                cd G:\\blog\\keefeWu.github.io &&\
                hexo new %s'%title_list[i]
        print(cmd)
        os.system(cmd)
        title_list[i] = title_list[i].replace('.', '-')
        title_list[i] = title_list[i].replace('.', '-')
        title_list[i] = title_list[i].replace('(', '-')
        title_list[i] = title_list[i].replace(')', '')
        html_data = deal_with_img(html_data, title_list[i], href_list[i])
        mdTxt = html2text.html2text(html_data)
        file = open('G:/blog/keefeWu.github.io/source/_posts/%s.md'%title_list[i], 'a', encoding="utf-8")
        file.write(mdTxt)
        file.close()
# main()