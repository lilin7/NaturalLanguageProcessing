import math

import query

def rank_docIDs_by_tf_idf(resultPostingsList, tokenizedWordList, global_inverted_index, N):
    # process for each docID to find BM25 score
    documentWithTfIdfValueDict = {}

    for eachDocID in resultPostingsList:
        sumTfIdfValue = 0
        documentFrequency = 0
        termFrequency = 0

        for tokenized_single_keyword in tokenizedWordList:
            postingList = query.get_postings_list(global_inverted_index, tokenized_single_keyword)

            if postingList:
                documentFrequency = len(postingList)
                termFrequency = global_inverted_index.get(tokenized_single_keyword, {}).get("postingsList_with_tf",{}).get(eachDocID, 0)

            else: # if the postings list is empty, means this term doesn't exist in this ID, so the BM25Score is 0
                continue

            if (documentFrequency == 0) or (termFrequency ==0):
                continue
            else:
                # for_single_word_and_given_doc
                tf_idf_value = round(termFrequency * round((math.log((round(N/documentFrequency, 3)),10)),3),3)
                sumTfIdfValue = sumTfIdfValue + tf_idf_value

        documentWithTfIdfValueDict[eachDocID] = round(sumTfIdfValue, 3)

    rankedDocumentDict = {k: v for k, v in
                          sorted(documentWithTfIdfValueDict.items(), key=lambda item: (-item[1],item[0]))}

    return rankedDocumentDict