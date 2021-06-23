from tabulate import tabulate

def print_table(rankedDocumentDict, docID_url_dict, rank_method):

    if rank_method == 'BM25':
        table_header = ['docID', 'URL', 'BM25 Score']
    elif rank_method == 'tf_idf':
        table_header = ['docID', 'URL', 'tf-idf']
    elif rank_method == 'goodness':
        table_header = ['docID', 'URL', 'Bonus Ranking - Goodness g(d)']
    else:
        table_header = ['docID', 'URL', '']

    table_data = []

    i = 0
    for each_docID in rankedDocumentDict.keys():
        if i<15:
            i = i + 1
            if str(each_docID) in docID_url_dict.keys():
                line_tuple = (each_docID, docID_url_dict[str(each_docID)], rankedDocumentDict[each_docID])
                table_data.append(line_tuple)
        else:
            break

    # print(tabulate(table_data, headers=table_header, tablefmt='grid', numalign="right",
    #                    colalign=("left", "left", "left")))

    print(tabulate(table_data, headers=table_header, tablefmt='grid'))
    return table_data # a list with 3 info

def print_ranked_result_to_file(table_data):
    dict_to_returns_file = {}
    for eachLine in table_data:
        dict_to_returns_file[eachLine[0]] = [eachLine[1], eachLine[2]]
    return dict_to_returns_file
