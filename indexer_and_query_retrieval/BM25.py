import nltk
import re
import math

import query

# calculate the BM25 ranking score for a term in a doc.
# need:
# N (number of documents) ok
# df (length of postings list of this term)
# k
# tf (how many times this term appears in this document)
# Ld (length of this doc)
# Lave (the average length of all documents in this collection) ok


def get_term_frequency_and_Ld(term, article):
    cleanArticleAsAListOfWords = list()  # cleaned article content as a list
    frequencyCounter = 0
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
        if containsLetterOrNumber != None:  # if there is any letter or number, return not None (return the first match e.g. <re.Match object; span=(1, 2), match='d'>)
            # containsNumber = patternNumber.search(eachWord)
            # if containsNumber != None:  # if there is any number
            #     cleanArticleAsAListOfWords.append(eachWord)
            # else:  # if no number
            cleanString = re.sub(r"[\#!\"$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]+\ *", " ",
                                 eachWord)  # replace the punctuation in each word with whitespace
            clearnWordList = cleanString.split()  # split and create a term for each part
            for eachCleanWord in clearnWordList:
                if eachCleanWord in stopwordsList:
                    continue
                cleanArticleAsAListOfWords.append(eachCleanWord)

    for eachCleanWord in cleanArticleAsAListOfWords:
        if eachCleanWord == term:
            frequencyCounter = frequencyCounter+1

    return [frequencyCounter, len(cleanArticleAsAListOfWords)]

def get_BM25_score_for_single_word_and_given_doc(N, df, tf, Ld, Lave, k1, b):
    return round(((math.log(round(N/df, 2), 10)) * (k1+1) * tf) / ( k1 * ( (1-b) + b * round(Ld /Lave, 2)) + tf), 3)

def rank_docIDs_by_BM25_score(resultPostingsList, tokenizedWordList, global_inverted_index, docIDContentDict, N, Lave, k1, b):
    # process for each docID to find BM25 score
    documentWithBM25RankingScoreDict = {}

    for eachDocID in resultPostingsList:
        sumBM25Score = 0

        for tokenized_single_keyword in tokenizedWordList:
            postingList = query.get_postings_list(global_inverted_index, tokenized_single_keyword)

            if postingList:
                documentFrequency = len(postingList)
                # documentFrequencyEarlier = global_inverted_index.get(tokenized_single_keyword, {}).get("df",0)
                # print("documentFrequency: ", documentFrequency)
                # print("documentFrequencyEarlier: ", documentFrequencyEarlier)

            else: # if the postings list is empty, means this term doesn't exist in this ID, so the BM25Score is 0
                continue

            eachDocIDstr = str(eachDocID)
            termFrequency, Ld = get_term_frequency_and_Ld(tokenized_single_keyword,
                                                               docIDContentDict[eachDocIDstr])

            # termFrequencyEarlier = global_inverted_index.get(tokenized_single_keyword, {}).get("postingsList_with_tf",{}).get(eachDocID, 0)
            # print("termFrequency: ", termFrequency)
            # print("termFrequencyEarlier: ", termFrequencyEarlier)

            BM25Score = get_BM25_score_for_single_word_and_given_doc(N=N, df=documentFrequency,
                                                                          tf=termFrequency, Ld=Ld, Lave=Lave,
                                                                          k1=k1, b=b)
            sumBM25Score = sumBM25Score + BM25Score

            # print('term:', tokenized_single_keyword, 'docID:', eachDocID, 'documentFrequency', documentFrequency, 'termFrequency:', termFrequency, 'Ld:', Ld, 'BM25Score:', BM25Score)
            documentWithBM25RankingScoreDict[eachDocID] = BM25Score

        documentWithBM25RankingScoreDict[eachDocID] = round(sumBM25Score, 3)

    rankedDocumentDict = {k: v for k, v in
                          sorted(documentWithBM25RankingScoreDict.items(), key=lambda item: (-item[1],item[0]))}
    # for eachID in rankedDocumentDict:
    #     print('[',eachID,']: ', rankedDocumentDict[eachID])

    return rankedDocumentDict #e.g. {1720: 2.437, 717: 2.405, 597: 2.197, 1911: 1.616, 200: 1.305, 922: 1.266, 79: 1.219}

