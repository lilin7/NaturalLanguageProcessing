import json
import datetime

import SPIMI
import query
import BM25
import tf_idf
import general_methods
import bonus_goodness_function

BLOCK_SIZE = 10000
k1 = 1.2
b = 0.3

# use the result from extractor
#docIDContentDict = extract.extract()
with open(r'../output/content_dict.json', encoding='utf-8') as json_file:
    docIDContentDict = json.load(json_file)

N = len(docIDContentDict.keys())  # for BM25, this is the N to calculate idf

startTime = datetime.datetime.now()

print('Begin creating indices...')
mini_inverted_index_dict, totalLengthOfAllArticles = SPIMI.creat_indexer(docIDContentDict, BLOCK_SIZE)

Lave = round(totalLengthOfAllArticles / N, 2) #for BM25

# merge many mini_inverted_indices to a global_inverted_index, write out
global_inverted_index = SPIMI.merge_indices(mini_inverted_index_dict)
#global_inverted_index_goodness = SPIMI.merge_indices_goodness(mini_inverted_index_dict_goodness)

endTime = datetime.datetime.now()
duration = endTime - startTime
print('My index takes this time to compile:', duration, '\n')

while (True):
    queryResultDict = {} # to store all queries and result, for final print
    user_input = input('\nPlease enter your query, enter 0 to exit:\n')

    if user_input == '0':
        print('You input is 0, exit. \nAll previous queries and the result are output to \"Returns.json\" file')
        #print('\nYour query history and the result with Naive Indexer is as below, and also saved to file: ' + 'query_result_history' + '.json.')
        break

    else:
        user_input_query = user_input
        tokenizedWordList = query.multiple_keyword_tokenize(user_input_query)

        unionPostingsList = query.process_multiple_keyword_query_get_result_docIDs(tokenizedWordList, global_inverted_index, '2')

        if not unionPostingsList:
            print("For your query, there is no result in the collection.")
            with open(r'../output/Returns.json', "a", encoding="utf−8") as output:
                print(json.dumps(user_input_query), file=output)
                print(json.dumps("For your query, there is no result in the collection."), file=output)
            continue

        print("postings list:")
        print(unionPostingsList)

        rankedDocumentByBM25Dict = BM25.rank_docIDs_by_BM25_score(unionPostingsList, tokenizedWordList,
                                                                  global_inverted_index, docIDContentDict, N, Lave, k1,
                                                                  b)

        rankedDocumentByTfIdfDict = tf_idf.rank_docIDs_by_tf_idf(unionPostingsList, tokenizedWordList, global_inverted_index, N)


        with open(r'../output/html_files/docID_url_dict.json', encoding='utf-8') as json_file:
            docID_url_dict = json.load(json_file)

        # bonus goodness function
        with open(r'../output/html_files/goodness_of_url_dict.json', encoding='utf-8') as json_file:
            goodness_of_url_dict = json.load(json_file)
        rankedDocumentByBonusGoodnessValue = bonus_goodness_function.rank_docIDs_by_goodness_function(unionPostingsList, docID_url_dict, goodness_of_url_dict)

        #print to console
        print('\nFor your query, top 15 result docID ranked using BM25 formula: ')
        print([*rankedDocumentByBM25Dict][0:15])
        print("\nTo also show the top 15 URL and its BM25 score:")
        table_data_bm25 = general_methods.print_table(rankedDocumentByBM25Dict, docID_url_dict, 'BM25')

        print('\nFor your query, top 15 result docID ranked using tf-idf value: ')
        print([*rankedDocumentByTfIdfDict][0:15])
        print("\nTo also show the top 15 URL and its tf-idf value:")
        table_data_tfidf =general_methods.print_table(rankedDocumentByTfIdfDict, docID_url_dict, 'tf_idf')

        print('\nFor your query, top 15 result docID ranked using bonus goodness function: ')
        print([*rankedDocumentByBonusGoodnessValue][0:15])
        print("\nTo also show the top 15 URL and its goodness score:")
        table_data_goodness = general_methods.print_table(rankedDocumentByBonusGoodnessValue, docID_url_dict, 'goodness')
        # table_data is a list, each element is (each_docID, docID_url_dict[str(each_docID)], rankedDocumentDict[each_docID])


        # output to Returns file as deliverable

        with open(r'../output/Returns.json', "a", encoding="utf−8") as output:
            print(json.dumps('User input query: '+user_input_query), file=output)
            print("URL ranked using BM25 formula: ", file=output)
            print(json.dumps(general_methods.print_ranked_result_to_file(table_data_bm25), indent=3), file=output)
            print("URL ranked using tf-idf value: ", file=output)
            print(json.dumps(general_methods.print_ranked_result_to_file(table_data_tfidf), indent=3), file=output)
            print("URL ranked using bonus goodness function: ", file=output)
            print(json.dumps(general_methods.print_ranked_result_to_file(table_data_goodness), indent=3), file=output)