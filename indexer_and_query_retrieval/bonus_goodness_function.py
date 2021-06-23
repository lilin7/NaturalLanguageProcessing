

def rank_docIDs_by_goodness_function(resultPostingsList, docID_url_dict, goodness_of_url_dict):
    documentWithBonusGoodnessValue = {}

    for eachDocID in resultPostingsList: #eachDocId is int

        url = docID_url_dict.get(str(eachDocID), '')
        goodness_score = goodness_of_url_dict.get(url, 0)

        documentWithBonusGoodnessValue[eachDocID] = goodness_score

    rankedDocumentDict = {k: v for k, v in
                          sorted(documentWithBonusGoodnessValue.items(), key=lambda item: (-item[1], item[0]))}

    return rankedDocumentDict  #key is int, value is int
