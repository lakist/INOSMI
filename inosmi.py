import urllib.request
import io
import os
import re
import html
import sys
        
#       _скачивание страницы_
def download_page(pageUrl):
    try:
        page = urllib.request.urlopen(pageUrl)
        text = page.read().decode('utf-8')
        return(text)
    except:
#        print('Error at', pageUrl)
        return(-1)


#       _очистка текста_
def clean_page(text):
    newText = re.compile('<div class="article-body"><p><em>.*?<div class="article-footer__source">', flags=re.DOTALL) 
    newText = newText.findall(text)
    regAside = re.compile('<aside class=.*?</aside>', flags=re.DOTALL) 
    regMdash = re.compile('&mdash;', flags=re.DOTALL)
    regRaquo = re.compile('&raquo;', flags=re.DOTALL)
    regLaquo = re.compile('&laquo;', flags=re.DOTALL)
    regNbsp = re.compile('&nbsp;', flags=re.DOTALL)
    regTag = re.compile('<.*?>', flags=re.DOTALL)
    newText = regNbsp.sub(" ", str(newText))
    newText = regMdash.sub("–", str(newText)) # заменяем тире
    newText = regRaquo.sub("»", str(newText)) # заменяем кавычки
    newText = regLaquo.sub("«", str(newText)) # заменяем кавычки
    newText = regAside.sub("", str(newText)) # удаляем ссылки на другие статьи
    newText = regTag.sub("", str(newText)) # удаляем тэги
    newText = newText[2:-2]
    newText = newText.replace (r"\n", "\n")
    return(newText)


#       _автор_
def author_(text):
    author=re.compile('<meta name="author".*?>', flags=re.DOTALL)
    author = author.findall(text)
    author = str(author)[31:-4]
    return(author)

#       _ссылка на оригинал_
def link_(text):
    link = re.compile('Оригинал публикации: <a href=.*?</a>', flags=re.DOTALL)
    link = link.findall(text)
    link = str(link)
    reg = re.compile('".*?"', flags=re.DOTALL)
    link = reg.search(link)
    return(link.group(0))

#       _название оригинала_
def orig_name_(text):
    name = re.compile('Оригинал публикации: <a href=.*?</a>', flags=re.DOTALL)
    name = name.findall(text)
    name = str(name)
    reg = re.compile('>.*?<', flags=re.DOTALL)
    name = reg.search(name)
    return(name.group(0))

#       _название перевода_
def name_(text):
    name = re.compile('<meta property="og:title" content=.*?">', flags=re.DOTALL)
    name = name.findall(text)
    name = str(name)
    reg = re.compile('".*?"', flags=re.DOTALL)
    name = reg.findall(name)[1]
    name = name[1:-1]
    return(name)

#       _создание метатаблицы_
def meta(page):
    tablePath = 'metadata.csv'
    path = "/Corpus"
    os.chdir(path)
    if not os.path.isfile(tablePath):
        create = open(tablePath, 'w', encoding='utf-8')
        create.close()
    table = open(tablePath, 'a', encoding='utf-8')
    infoString = '%s\t%s\t%s\t%s'
    author = author_(page) # автор
    name = name_(page) # название перевода
    link = "/Corpus/"+ name + ".txt"
    orig_name = orig_name_(page)[1:-1] # название оригинала
    table.write(infoString % (author, name, orig_name, link) + '\r\n')
    table.close()
    return (0)

#       _сохранение документа_
def direct(name, page):
    path = "/Corpus"
    os.chdir(path)
    ouf=open(name+".txt", "w", encoding="utf-8")
    ouf.write(page)
    ouf.close()
    return (0)

#       _очистка иностранного текста_
def orig_clean_page():
    path = "/Corpus"
    os.chdir(path)
    ouf=open("draft.txt", "r", encoding="utf-8")
    text = ouf.readlines()
    newText = ''
    for i in range (len(text)):
        if text[i].count ('{') + text[i].count ('}') + text[i].count ('[') + text[i].count (']') + text[i].count ('var') + text[i].count ('=') + text[i].count ('/') + text[i].count ('|') + text[i].count ("'") + text[i].count ("*")  + text[i].count ("_") + text[i].count ("#") + text[i].count ("$") + text[i].count ("()") == 0:
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
    return (newText)


def main ():
    print("введите url")
    commonUrl = input()
    translated = download_page(commonUrl) #скачиваем перевод
    meta(translated)
    name = name_(translated)
    orig_name = orig_name_(translated)[1:-1]
    link = link_(translated)[1:-1]
    origin = download_page(link) #скачиваем оригинал
    translated = clean_page(translated)
    direct(name,translated)
    direct("draft",origin)
    newText = orig_clean_page()
    direct(orig_name,newText)
    os.remove('/Corpus/draft.txt')
    return (0)

main()
