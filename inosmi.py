import urllib.request
import io
import os
import re
import html
import sys
import time

regText = re.compile('<div class="article-body">.*?<div class="article-footer__source">', flags=re.DOTALL)
regAside = re.compile('<aside class=.*?</aside>', flags=re.DOTALL) 
regTag = re.compile('<.*?>', flags=re.DOTALL)
regOrig_name = re.compile(">.*?</a>", flags=re.DOTALL)
regAuthor = re.compile('<meta name="author".*?>', flags=re.DOTALL)
regLink = re.compile('Оригинал публикации: <a href=.*?</a>', flags=re.DOTALL)
regHref = re.compile('<a href=".*?"', flags=re.DOTALL)
regName = re.compile('<meta property="og:title" content=.*?">', flags=re.DOTALL)
regCont = re.compile('content=".*?"', flags=re.DOTALL)
regUrl = re.compile('article-title"><a href="/.*?/.*?/.*?.html', flags=re.DOTALL)
regT = re.compile('\t', flags=re.DOTALL)

def get_charset(header):
    match = re.search(r'charset=([^\s;]+)', header)
    if match:
        return match.group(1).strip('"\'').lower()


#       _скачивание страницы_
def download_page(pageUrl):
    try:
        with urllib.request.urlopen(pageUrl) as data:
            charset = get_charset(data.getheader('content-type'))
            text = data.read().decode(charset)
        return text
    except:
#        print('Error at', pageUrl)
        return -1


#       _очистка текста_
def clean_page(text):
    newText = regText.search(text)
    newText = newText.group(0)
    newText = regAside.sub("", newText) # удаляем ссылки на другие статьи
    newText = regTag.sub("", newText) # удаляем тэги
    newText = newText.replace (r"\n", "\n")
    newText = html.unescape(newText)
    return newText


#       _автор_
def Author(text):
    author = regAuthor.search(text)
    if author:
        return author.group(0)[31:-4]
    else:
        return 0

#       _ссылка на оригинал_
def Link(text):
    link = regLink.search(text)
    link = link.group(0)
    link = regHref.search(link)
    if link:
        return link.group(0)
    else:
        return 0

#       _название оригинала_
def Orig_name(text):
    name = regLink.search(text)
    name = name.group(0)
    name = regOrig_name.search(name)
    if name:
        return name.group(0)
    else:
        return 0

#       _название перевода_
def Name(text):
    name = regName.search(text)
    name = name.group(0)
    name = regCont.search(name)
    if name:
        return name.group(0)[9:-1]
    else:
        return 0

#       _создание метатаблицы_
def meta(page):
    tablePath = 'metadata.csv'
    path = "/Corpus"
    os.chdir(path)
    if not os.path.isfile(tablePath):
        create = open(tablePath, 'w', encoding='utf-8')
        create.close()
    table = open(tablePath, 'a', encoding='utf-8')
    infoString = '%s\t%s\t%s\t%s\t%s'
    author = Author(page) # автор
    name = Name(page) # название перевода
    link = "/Corpus/inosmi/"+ name + ".txt"
    orig_name = Orig_name(page)[1:-4] # название оригинала
    orig_link = "/Corpus/original/"+ orig_name + ".txt"
    table.write(infoString % (author, name, orig_name, link, orig_link) + '\r\n')
    table.close()
    return 0

#       _сохранение документа_
def direct(name, page, folder):
    path = "/Corpus"+ folder
    os.chdir(path)
    if name.find('.')>0:
        name=name[:name.find('.')]
    ouf=open(name+".txt", "w", encoding="utf-8")
    ouf.write(page)
    ouf.close()
    return 0

#       _очистка иностранного текста_
def orig_clean_page(text):
        newText = regTag.sub("", text) # удаляем тэги
        newText = regT.sub("", newText) # удаляем табуляции
        while newText.count (' \n') != 0:
            newText = newText.replace (" \n", " ") 
        while newText.count ('\n\n') != 0:
            newText = newText.replace ("\n\n", "\n") # удаляем лишние переводы строки
        while newText.count ('  ') != 0:
            newText = newText.replace ("  ", " ") # удаляем двойные пробелы
        return newText

#       _краулер_
def crawler(Urls, a):
    b = len(Urls)
    for i in range(a, b):
        print(i, Urls[i][25:])
        page = download_page("http://inosmi.ru/" + Urls[i][25:])
        NewUrls = regUrl.findall(page)
        j = 0
        for j in range (len(NewUrls)):
            if NewUrls[j] not in Urls:
                if len(Urls) < 20:
                    Urls.append(NewUrls[j])
        time.sleep(2) 
    if len(Urls) < 20:
        crawler (Urls, b)
    return Urls          


def main ():
    inosmi = download_page("http://inosmi.ru/")
    Urls = regUrl.findall(inosmi)
    Urls = set(Urls)
    Urls = list(Urls)
    Urls = crawler(Urls, 0)
    for i in range (len (Urls)):
            if  (Urls[i][25:30])!="overv" and (Urls[i][25:30])!="video":
                translated = download_page("http://inosmi.ru/" + Urls[i][25:]) #скачиваем перевод
                name = Name(translated)
                orig_name = Orig_name(translated)
                if orig_name != 0 and orig_name[1:5] != 'http': 
                    link = Link(translated)[9:-1]
                    orig_name = orig_name[1:-4]
                    origin = download_page(link) #скачиваем оригинал
                    if origin != -1:
                        origin = orig_clean_page(origin)
                        if origin != "":
                            meta(translated)
                            translated = clean_page(translated)
                            direct(name,translated, "/inosmi")
                            direct(orig_name,origin, "/original")
    return (0)

main()
