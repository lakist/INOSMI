#       _очистка иностранного текста_
def orig_clean_page():
    path = "/Corpus"
    os.chdir(path)
    ouf=open("draft.txt", "r", encoding="utf-8")
    text = ouf.readlines()
    newText = ''
    for i in range (len(text)):
        if text[i].count ('{') + text[i].count ('}') + text[i].count ('[') + text[i].count (']') + text[i].count ('var') + text[i].count ('=') + text[i].count ('/') + text[i].count ('|') + text[i].count ("*")  + text[i].count ("_") + text[i].count ("#") + text[i].count ("$") + text[i].count ("()") == 0:
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
