import re
import nltk

def get_postings_list(invertedIndex, word):
    if not (word in invertedIndex.keys()): # the query term doesn't exist in the collection
        return []
    else:
        postingList = invertedIndex[word].get("postingsList_with_tf", {}).keys()
        return postingList



def multiple_keyword_tokenize(multiple_keywords_query):
    processedWordList = list()

    wordsList = nltk.word_tokenize(multiple_keywords_query)

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
        if containsLetterOrNumber != None:  # if there is any letter or number, return not None (return the first match e.g. <re.Match object; span=(1, 2), match='d'>)
            # containsNumber = patternNumber.search(eachWord)
            # if containsNumber != None:  # if there is any number
            #     processedWordList.append(eachWord)
            # else:  # if no number
                cleanString = re.sub(r"[\#!\"$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]+\ *", " ",
                                     eachWord)  # replace the punctuation in each word with whitespace
                clearnWordList = cleanString.split()  # split and create a term for each part
                for eachCleanWord in clearnWordList:
                    if eachCleanWord in stopwordsList:
                        continue
                    processedWordList.append(eachCleanWord)
    return processedWordList

def process_multiple_keyword_query_get_result_docIDs(tokenizedWordList, global_inverted_index, case_number):
    listOfAllPostingList = []
    # find the postings list for all tokens in the query
    for eachWord in tokenizedWordList:
        postingList = get_postings_list(global_inverted_index, eachWord)
        #print('term:', eachWord, 'postingsList', postingList) # for test, print each postings list to check
        listOfAllPostingList.append(postingList)

    if not listOfAllPostingList: #no result
        return []

    # (b) a query consisting of several keywords for BM25
    if case_number == "2":
        # find intersection of all postings list for all tokens in the query
        unionPostingsList = listOfAllPostingList[0]
        for each in listOfAllPostingList:
            unionPostingsList = sorted(list(set(unionPostingsList) | set(each)))
        return unionPostingsList #sorted, removed duplicate

    # (c). a multiple keyword query returning documents containing all the keywords (AND), for unranked Boolean retrieval
    elif case_number == "3":
        # find intersection of all postings list for all tokens in the query
        intersectionPostingsList = listOfAllPostingList[0]
        for each in listOfAllPostingList:
            intersectionPostingsList = sorted(list(set(intersectionPostingsList) & set(each)))
        return intersectionPostingsList #sorted, removed duplicate

    # 4. A multiple keywords query returning documents containing at least one keyword (OR), where documents are ordered by how many keywords they contain;'
    elif case_number == "4":
        rawUnionPostingsList = []
        for each in listOfAllPostingList:
            rawUnionPostingsList = rawUnionPostingsList + each
        return rawUnionPostingsList # [1, 7, 3, 4, 5, 1, 3, 5, 6, 3, 5, 6, 7] a union postings list with duplicate and not sorted

    else:
        return []

def rank_docIDs_by_occurence(rawUnionPostingsList):
    howManyKeywordsDocumentsContainDict = {}
    for each in rawUnionPostingsList:
        if each in howManyKeywordsDocumentsContainDict.keys():
            occurence = howManyKeywordsDocumentsContainDict[each]
            occurence = occurence + 1
            howManyKeywordsDocumentsContainDict[each] = occurence
        else:
            howManyKeywordsDocumentsContainDict[each] = 1

    rankedDocumentByOccurenceDict = {k: v for k, v in
                                     sorted(howManyKeywordsDocumentsContainDict.items(),
                                            key=lambda item: (-item[1], item[0]), )}
    return rankedDocumentByOccurenceDict