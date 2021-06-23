from bs4 import BeautifulSoup
import re
import json

import preprocess


def extract():
    html_dict = {}  # store all raw html files

    dirPath = r'../output/html_files'
    for docID_and_html_file_content in preprocess.block_reader(dirPath):
        html_dict[docID_and_html_file_content[0]] = docID_and_html_file_content[1]
        if docID_and_html_file_content[0]%100 == 0:
            print('reading html file', docID_and_html_file_content[0])

    docIDContentDict = {}
    for each_docID in html_dict.keys():
        if each_docID%100 == 0:
            print('extracting html file', each_docID)
        each_html_file_content = html_dict[each_docID]
        soup = BeautifulSoup(each_html_file_content, features="html.parser")
        # allArticles = soup.find_all('reuters')
        # content = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'li', 'span', 'div', 'p', 'title'])
        #ontent = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'p', 'li'])
        content = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'p'])
        #content = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'li', 'span', 'div', 'ul', 'ol', 'tr', 'td', 'th'])


        all_content_list = []
        for each_item in content:
            content_str = each_item.text
            dryText = re.sub(r"[\n\r\t ]+", " ", content_str)
            #print(dryText)

            if dryText not in all_content_list:  # to avoid duplicate title, etc.
                all_content_list.append(dryText)

        all_content_str = ' '.join(all_content_list)
        docIDContentDict[each_docID] = all_content_str

    with open(r'../output/content_dict' + ".json", "w", encoding=" utf−8") as file:
        json.dump(docIDContentDict, file, ensure_ascii=False)
        # print(docIDContentDict, file=file) #works, but with "\xa00"
    # json.dump(docIDContentDict, open('./content_dict' + ".json", "w", encoding=" utf−8"), indent=3) #works, but with "\u2000"

    return docIDContentDict