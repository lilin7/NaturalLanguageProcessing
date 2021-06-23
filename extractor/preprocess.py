import json
import os
from bs4 import BeautifulSoup
import re
import nltk
import string

'''
Pre-process methods

This class implements methods for pre-processing data, using the methods I developed for project 1
Those methods will be called from class main.
'''

# block 1:
# read sgm files in the folder path, generate the content of sgm files one by one
def block_reader(path):

    files = os.listdir(path)

    for file in files:
        if ((not os.path.isdir(file)) and (file.endswith(".html"))) : #only open the ones which are not folders, and is html file

            with open(path + '/' + file, 'rb') as f:
                data = f.read()
                soup = BeautifulSoup(data, features="html.parser")
                html_file_content = str(soup)

                file_name = file.replace(".html", "")
                if not html_file_content == "":
                    yield [int(file_name), html_file_content]  # the content of one sgm file
                else:
                    continue


# block 2:
# segment each article in each sgm file
def block_document_segmenter(SGMFileContentList):
    for eachSgmFile in SGMFileContentList:
        soup = BeautifulSoup(eachSgmFile, features="html.parser")
        allArticles = soup.find_all('reuters')

        for eachArticle in allArticles:
            document_text = str(eachArticle).replace('<reuters', '<REUTERS').replace('</reuters>', '</REUTERS>')
            yield document_text


# block 3:
# extract new id of an article as docID, and the whole text of the article
def block_extractor(rawArticleList):
        for eachArticleWithTags in rawArticleList:
            soup = BeautifulSoup(eachArticleWithTags, features="html.parser")

            newid = soup.reuters.get('newid')

            textOfArticle = ""

            for find in soup.find_all('text'):
                titleStr = ''
                contentStr = ''

                if not find == "":

                    if find.title or find.body:
                        if find.title:
                            titleStr = find.title.text.replace("\n"," ")

                        if find.body:
                            contentStr = find.body.text.replace("\n"," ")
                    else:
                        contentStr = find.text.replace("\n"," ")

                    textOfArticle = textOfArticle + titleStr + " " + contentStr

            content_dict = {"ID": int(newid), "TEXT": textOfArticle}  # Sample dictionary structure of output
            yield content_dict


#block 4: tokenize each article, if the token is pure punctuation, remove it
def block_tokenizer(id, article):
        wordsList = nltk.word_tokenize(article)

        # regular expression to check if the token contains any letter or number.
        # If does NOT contain a single letter or number, consider as punctuation and not put into consideration
        pattern = re.compile('[A-Za-z0-9]')
        patternNumber = re.compile('[0-9]')

        stopwordsList = []
        with open('./stopwords30.txt') as f:
            for line in f.readlines():
                stopword = line.strip()
                stopword = stopword.lower()
                stopwordsList.append(stopword)

        for eachWord in wordsList:
            eachWord = eachWord.strip()
            eachWord = eachWord.lower()
            if eachWord in stopwordsList:
                continue

            containsLetterOrNumber = pattern.search(eachWord)
            if containsLetterOrNumber != None: # if there is any letter or number, return not None (return the first match e.g. <re.Match object; span=(1, 2), match='d'>)
                # containsNumber = patternNumber.search(eachWord)
                # if containsNumber != None: # if there is any number
                #     token_tuple = (id, eachWord)  # Sample id, token tuple structure of output
                #     yield token_tuple
                # else: #if no number
                    cleanString = re.sub(r"[\#!\"$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]+\ *", " ", eachWord) #replace the punctuation in each word with whitespace
                    clearnWordList = cleanString.split() #split and create a term for each part
                    for eachCleanWord in clearnWordList:
                        token_tuple = (id, eachCleanWord)  # Sample id, token tuple structure of output
                        yield token_tuple