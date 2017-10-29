import urllib.request
import io
import os
import re
import html
import sys
import time

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
    newText = re.compile('<div class="article-body">.*?<div class="article-footer__source">', flags=re.DOTALL) 
    newText = newText.search(text)
    newText = newText.group(0)
    regAside = re.compile('<aside class=.*?</aside>', flags=re.DOTALL) 
    regMdash = re.compile('&mdash;', flags=re.DOTALL)
    regRaquo = re.compile('&raquo;', flags=re.DOTALL)
    regLaquo = re.compile('&laquo;', flags=re.DOTALL)
    regNbsp = re.compile('&nbsp;', flags=re.DOTALL)
    regQuot = re.compile('&quot;', flags=re.DOTALL)
    regTag = re.compile('<.*?>', flags=re.DOTALL)
    newText = regNbsp.sub(" ", str(newText))
    newText = regMdash.sub("–", str(newText)) # заменяем тире
    newText = regQuot.sub('"', str(newText)) # заменяем кавычки
    newText = regRaquo.sub("»", str(newText)) # заменяем кавычки
    newText = regLaquo.sub("«", str(newText)) # заменяем кавычки
    newText = regAside.sub("", str(newText)) # удаляем ссылки на другие статьи
    newText = regTag.sub("", str(newText)) # удаляем тэги
    newText = newText.replace (r"\n", "\n")
    newText = str(newText)
    return newText


#       _автор_
def author_(text):
    author = re.compile('<meta name="author".*?>', flags=re.DOTALL)
    author = author.findall(text)
    author = str(author)[31:-4]
    return author 

#       _ссылка на оригинал_
def link_(text):
    link = re.compile('Оригинал публикации: <a href=.*?</a>', flags=re.DOTALL)
    link = link.findall(text)
    link = str(link)
    reg = re.compile('<a href=".*?"', flags=re.DOTALL)
    link = reg.search(link)
    if link == None:
        return 0
    else:
        return link.group(0)

#       _название оригинала_
def orig_name_(text):
    name = re.compile('Оригинал публикации: <a href=.*?</a>', flags=re.DOTALL)
    name = name.findall(text)
    name = str(name)
    reg = re.compile(">.*?</a>", flags=re.DOTALL)
    name = reg.search(name)
    if name == None:
        return 0
    else:
        return name.group(0)

#       _название перевода_
def name_(text):
    name = re.compile('<meta property="og:title" content=.*?">', flags=re.DOTALL)
    name = name.findall(text)
    name = str(name)
    reg = re.compile('".*?"', flags=re.DOTALL)
    name = reg.findall(name)[1]
    name = name[1:-1]
    return name

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
    author = author_(page) # автор
    name = name_(page) # название перевода
    link = "/Corpus/inosmi/"+ name + ".txt"
    orig_name = orig_name_(page)[1:-4] # название оригинала
    orig_link = "/Corpus/original/"+ orig_name + ".txt"
    table.write(infoString % (author, name, orig_name, link, orig_link) + '\r\n')
    table.close()
    return 0

#       _сохранение документа_
def direct(name, page, folder):
    path = "/Corpus"+ folder
    os.chdir(path)
    ouf=open(name+".txt", "w", encoding="utf-8")
    ouf.write(page)
    ouf.close()
    return 0

#       _очистка иностранного текста_
def orig_clean_page(text):
    newText = re.compile('<p>.*?</p>"', flags=re.DOTALL) 
    newText = newText.findall(text)
    if newText == []:
        newText = text
        direct("draft",text,"")
        newText = orig_clean_page_two()
        os.remove('/Corpus/draft.txt')
    else:
        newText = '/n'.join(newText)
        regMdash = re.compile('&mdash;', flags=re.DOTALL)
        regRaquo = re.compile('&raquo;', flags=re.DOTALL)
        regLaquo = re.compile('&laquo;', flags=re.DOTALL)
        regNbsp = re.compile('&nbsp;', flags=re.DOTALL)
        regQuot = re.compile('&quot;', flags=re.DOTALL)
        regTag = re.compile('<.*?>', flags=re.DOTALL)
        newText = regNbsp.sub(" ", str(newText))
        newText = regMdash.sub("–", str(newText)) # заменяем тире
        newText = regQuot.sub('"', str(newText)) # заменяем кавычки
        newText = regRaquo.sub("»", str(newText)) # заменяем кавычки
        newText = regLaquo.sub("«", str(newText)) # заменяем кавычки
        newText = regTag.sub("", str(newText)) # удаляем тэги
        newText = newText.replace (r"\n", "\n")
        newText = str(newText)
    return newText

def orig_clean_page_two():
    path = "/Corpus"
    os.chdir(path)
    ouf=open("draft.txt", "r", encoding="utf-8")
    text = ouf.readlines()
    newText = ''
    for i in range (len(text)):
        if text[i].count ('{') + text[i].count ('}') + text[i].count ('[') + text[i].count (']') + text[i].count ('var') + text[i].count ('=') + text[i].count ('/') + text[i].count ('|') + text[i].count ("*")  + text[i].count ("_") + text[i].count ("#") + text[i].count ("()") == 0:
            regTag = re.compile('<.*?>', flags=re.DOTALL)
            newText = regTag.sub("", str(newText)) # удаляем тэги
            regT = re.compile('\t', flags=re.DOTALL)
            newText = regT.sub("", str(newText)) # удаляем табуляции
            while newText.count (' \n') != 0:
                regN = re.compile(' \n', flags=re.DOTALL)
                newText = regN.sub(" ", str(newText)) 
            while newText.count ('\n\n') != 0:
                regN = re.compile('\n\n', flags=re.DOTALL)
                newText = regN.sub("\n", str(newText)) 
            while newText.count ('  ') != 0:
                regN = re.compile('  ', flags=re.DOTALL)
                newText = regN.sub(" ", str(newText)) 
            newText = newText + text[i]
    ouf.close()
    return newText

        
#       _краулер_
def crawler(Urls, a):
    for i in range(len(Urls)):
        print(i, Urls[i][25:])
        page = download_page("http://inosmi.ru/" + Urls[i][25:])
        regUrl = re.compile('article-title"><a href="/.*?/.*?/.*?.html', flags=re.DOTALL)
        NewUrls = regUrl.findall(page)
        j = 0
        for j in range (len(NewUrls)):
            if NewUrls[j] not in Urls:
                if len(Urls) < 200:
                    Urls.append(NewUrls[j])
        time.sleep(2) 
    if len(Urls) < 200:
        crawler (Urls, len(Urls))
    return Urls           


def main ():
    inosmi = download_page("http://inosmi.ru/")
    regUrl = re.compile('article-title"><a href="/.*?/.*?/.*?.html', flags=re.DOTALL)
    Urls = regUrl.findall(inosmi)
    Urls = set(Urls)
    Urls = list(Urls)
    Urls = crawler(Urls, 0)
    for i in range (len (Urls)):
            if  (Urls[i][25:30])!="overv" and (Urls[i][25:30])!="video":
                translated = download_page("http://inosmi.ru/" + Urls[i][25:]) #скачиваем перевод
                name = name_(translated)
                orig_name = orig_name_(translated)
                if orig_name != 0 and orig_name[1:5] != 'http': 
                    link = link_(translated)[9:-1]
                    orig_name = orig_name[1:-4]
                    origin = download_page(link) #скачиваем оригинал
                    if origin != -1:
                        origin = orig_clean_page(origin)
                        print (origin)
                        if origin != "":
                            meta(translated)
                            translated = clean_page(translated)
                            direct(name,translated, "/inosmi")
                            direct(orig_name,origin, "/original")
    return (0)

main()
