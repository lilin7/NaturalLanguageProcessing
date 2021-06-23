import json
import preprocess
import datetime

def create_mini_inverted_index(mini_inverted_index, tokenDocIDPair):
    if not (tokenDocIDPair[0] in mini_inverted_index.keys()):  # a new term
        postingsList_with_tf_value = {}
        postingsList_with_tf_value[tokenDocIDPair[1]] = 1 #{1:1} docID 1 has tf=1
        info_dict = {}
        info_dict["df"] = 1
        info_dict["postingsList_with_tf"] = postingsList_with_tf_value
        mini_inverted_index[tokenDocIDPair[0] ] = info_dict

    else:  # not a new term
        info_dict = mini_inverted_index[tokenDocIDPair[0]]
        postingsList_with_tf_value = info_dict["postingsList_with_tf"] #get existing data like {1: 2,   2: 2,   3: 2}

        if tokenDocIDPair[1] not in postingsList_with_tf_value.keys(): #first time of this docID
            postingsList_with_tf_value[tokenDocIDPair[1]] = 1
            info_dict["df"] = len(postingsList_with_tf_value.keys())

            postingsList_with_tf_value = {k: v for k, v in sorted(postingsList_with_tf_value.items(),
                                                                               key=lambda item: (-item[1], item[0]))}
            info_dict["postingsList_with_tf"] = postingsList_with_tf_value
            mini_inverted_index[tokenDocIDPair[0]] = info_dict

        else: #only increment the tf of this docID
            original_tf = postingsList_with_tf_value[tokenDocIDPair[1]]
            updated_tf = original_tf + 1
            postingsList_with_tf_value[tokenDocIDPair[1]] = updated_tf

            info_dict["df"] = len(postingsList_with_tf_value.keys())
            postingsList_with_tf_value = {k: v for k, v in sorted(postingsList_with_tf_value.items(),
                                                                               key=lambda item: (-item[1], item[0]))}
            info_dict["postingsList_with_tf"] = postingsList_with_tf_value
            mini_inverted_index[tokenDocIDPair[0]] = info_dict

    mini_inverted_index = {k: mini_inverted_index[k] for k in sorted(mini_inverted_index)}

    return mini_inverted_index # return a dict as the inverted index

def create_mini_inverted_index_goodness(mini_inverted_index_goodness, tokenDocIDPair):
    with open(r'../output/html_files/docID_url_dict.json') as json_file:
        docID_url_dict = json.load(json_file)

    with open(r'../output/html_files/goodness_of_url_dict.json') as json_file:
        goodness_of_url_dict = json.load(json_file)

    if not (tokenDocIDPair[0] in mini_inverted_index_goodness.keys()):  # a new term
        postingsList_with_goodness_value = {}

        url = docID_url_dict.get(str(tokenDocIDPair[1]), '')
        postingsList_with_goodness_value[tokenDocIDPair[1]] = goodness_of_url_dict.get(url, 0) #{1:10} docID 1 has goodness value of 20

        info_dict = {}
        info_dict["df"] = 1
        postingsList_with_goodness_value = {k: v for k, v in sorted(postingsList_with_goodness_value.items(),
                                                              key=lambda item: (-item[1], item[0]))}
        info_dict["postingsList_with_goodness_value"] = postingsList_with_goodness_value
        mini_inverted_index_goodness[tokenDocIDPair[0]] = info_dict

    else:  # not a new term
        info_dict = mini_inverted_index_goodness[tokenDocIDPair[0]]

        postingsList_with_goodness_value = info_dict["postingsList_with_goodness_value"] #get existing data like {1: 10,   2: 20,   3: 5}

        if tokenDocIDPair[1] not in postingsList_with_goodness_value.keys(): #first time of this docID, e.g. 4
            postingsList_with_goodness_value[tokenDocIDPair[1]] = goodness_of_url_dict.get(docID_url_dict.get(str(tokenDocIDPair[1]), ''), 0) #{1:10} docID 1 has goodness value of 20
            info_dict["df"] = len(postingsList_with_goodness_value.keys())
            postingsList_with_goodness_value = {k: v for k, v in sorted(postingsList_with_goodness_value.items(),
                                                                        key=lambda item: (-item[1], item[0]))}
            info_dict["postingsList_with_goodness_value"] = postingsList_with_goodness_value
            mini_inverted_index_goodness[tokenDocIDPair[0]] = info_dict

        #else: #if doc ID appeared before, do nothing, as the goodness value won't change
    mini_inverted_index_goodness = {k: mini_inverted_index_goodness[k] for k in sorted(mini_inverted_index_goodness)}
    return mini_inverted_index_goodness # return a dict as the inverted index

def creat_indexer(docIDContentDict, BLOCK_SIZE):
    totalLengthOfAllArticles = 0
    blockSizeCounter = 0
    blockNumberCounter = 0

    mini_inverted_index = {}  # a container for the inverted index of each 500/block size token-docID pairs
    mini_inverted_index_dict = {}  # key is block number, value is a dict: the mini inverted index for this block

    # mini_inverted_index_goodness = {}
    # mini_inverted_index_dict_goodness = {}

    # while there are still more documents to be processed, accepts a document as a list of tokens and outputs term-documentID pairs
    for each in docIDContentDict.keys():
        eachDocID = int(each)
        tokenList = []
        for token_tuple in preprocess.block_tokenizer(eachDocID, docIDContentDict[each]):
            tokenList.append(token_tuple)
        # tokenList is a list of tokens (docID, token) for one article

        totalLengthOfAllArticles = totalLengthOfAllArticles + len(
            tokenList)  # for BM25, add the number of tokens of one article

        for oneDocIDTerm in tokenList:
            if (len(oneDocIDTerm) == 2):
                pair = [oneDocIDTerm[1], oneDocIDTerm[0]]  # term-ID pairs [a,1]

                if blockSizeCounter < BLOCK_SIZE:  # block not full, i.e. token-docID pairs not exceeding 500/block size
                    blockSizeCounter = blockSizeCounter + 1
                    mini_inverted_index = create_mini_inverted_index(mini_inverted_index, pair)

                    #mini_inverted_index_goodness = create_mini_inverted_index_goodness(mini_inverted_index_goodness, pair)

                    # if blockSizeCounter%1000 == 0:
                    #     print('blockSizeCounter', blockSizeCounter)

                else:  # blockSizeCounter=500, there has passed 500 token-id pairs and created their inverted index
                    # put the mini_inverted_index of the finished block to dict mini_inverted_index_dict
                    mini_inverted_index_dict[blockNumberCounter] = mini_inverted_index
                    startTime = datetime.datetime.now()
                    print(startTime, 'Created mini inverted index block', blockNumberCounter)
                    # mini_inverted_index_dict_goodness [blockNumberCounter] = mini_inverted_index_goodness
                    # print('Created mini inverted index goodness block', blockNumberCounter)

                    with open(r"../output/Block" + str(blockNumberCounter) + ".txt", "w",
                              encoding=" utf−8") as output:
                        for k, v in mini_inverted_index.items():
                            print("%-20s %-20s" % (k, v), file=output)

                    # need to count for next block
                    # print('blockNumberCounter', blockNumberCounter)
                    mini_inverted_index = {}  # initialize the container for the inverted index of next 500/block size token-docID pairs
                    #mini_inverted_index_goodness = {}
                    blockSizeCounter = 0
                    blockNumberCounter = blockNumberCounter + 1
            else:
                continue

    # for the last block, create mini-index and write to file
    if mini_inverted_index:  # after all article, if there is still something left in the mini_inverted_index, means the last block
        mini_inverted_index_dict[blockNumberCounter] = mini_inverted_index
        with open(r"../output/Block" + str(blockNumberCounter) + ".txt", "w", encoding=" utf−8") as output:
            for k, v in mini_inverted_index.items():
                print("%-20s %-20s" % (k, v), file=output)

    assert (len(
        mini_inverted_index_dict.keys()) == blockNumberCounter + 1)  # as there is a blockNumberCounter=0 for block 0

    # if mini_inverted_index_goodness:
    #     mini_inverted_index_dict_goodness [blockNumberCounter] = mini_inverted_index_goodness
    #
    # assert (len(
    #     mini_inverted_index_dict_goodness.keys()) == blockNumberCounter + 1)

    print('Created:', blockNumberCounter+1, 'blocks.')
    print('Write all blocks to disk for verification')
    return [mini_inverted_index_dict, totalLengthOfAllArticles]

def merge_indices (mini_inverted_index_dict):
    global_inverted_index = {}

    for eachBlockNumber in mini_inverted_index_dict.keys():
        mini_inverted_index = mini_inverted_index_dict [eachBlockNumber] # a dict: e.g. {'a': {'df': 3, 'postingsList_with_tf': {1: 2, 2: 2, 3: 2}}, 'b': {'df': 1, 'postingsList_with_tf': {4: 1}}}

        # merge all mini_inverted_indices
        # global_inverted_index =  {k: sorted(list(set(mini_inverted_index.get(k, []) + global_inverted_index.get(k, []))))
        #             for k in set(list(mini_inverted_index.keys()) + list(global_inverted_index.keys()))}
        startTime = datetime.datetime.now()
        print(startTime, 'merging mini_inverted_index', eachBlockNumber, 'to global inverted index...')
        for k in set(list(mini_inverted_index.keys()) + list(global_inverted_index.keys())): #term, e.g. "a"
            postingsList_with_tf_value_mini = mini_inverted_index.get(k, {}).get("postingsList_with_tf", {}) #{1: 2, 2: 2, 3: 2}
            postingsList_with_tf_value_global = global_inverted_index.get(k, {}).get("postingsList_with_tf", {}) #{1: 2, 2: 2, 3: 2}
            postingsList_with_tf_value_new = {k: postingsList_with_tf_value_mini.get(k, 0) + postingsList_with_tf_value_global.get(k, 0) for k in set(postingsList_with_tf_value_mini) | set(postingsList_with_tf_value_global)}
            postingsList_with_tf_value_sorted_by_tf = {k: v for k, v in sorted(postingsList_with_tf_value_new.items(), key=lambda item: (-item[1], item[0]))}

            info_dict={}
            info_dict["df"] = len(postingsList_with_tf_value_sorted_by_tf.keys())
            info_dict["postingsList_with_tf"] = postingsList_with_tf_value_sorted_by_tf
            global_inverted_index[k] = info_dict


    global_inverted_index = {k: global_inverted_index[k] for k in sorted(global_inverted_index)}


    with open(r"../output/global_inverted_index.txt", "w", encoding=" utf−8") as output:
        for k, v in global_inverted_index.items():
            print("%-20s %-20s" % (k, v), file=output)
    print('\nMerged all mini inverted indices in all blocks to a global inverted index.')
    print('Global inverted index write out to file \"global_inverted_index.txt\"\n')

    return global_inverted_index

def merge_indices_goodness (mini_inverted_index_dict_goodness):
    global_inverted_index_goodness = {}

    for eachBlockNumber in mini_inverted_index_dict_goodness.keys():
        mini_inverted_index_goodness = mini_inverted_index_dict_goodness [eachBlockNumber] # a dict: e.g. {'a': {'df': 3, 'postingsList_with_tf': {1: 2, 2: 2, 3: 2}}, 'b': {'df': 1, 'postingsList_with_tf': {4: 1}}}
        print('merging mini_inverted_index_goodness', eachBlockNumber, 'to global inverted index...')
        for k in set(list(mini_inverted_index_goodness.keys()) + list(global_inverted_index_goodness.keys())):  # term, e.g. "a"
            postingsList_with_goodness_value_mini = mini_inverted_index_goodness.get(k, {}).get("postingsList_with_goodness_value",
                                                                                 {})  # {1: 2, 2: 2, 3: 2}
            postingsList_with_goodness_value_global = global_inverted_index_goodness.get(k, {}).get("postingsList_with_goodness_value",
                                                                                     {})  # {1: 2, 2: 2, 3: 2}
            postingsList_with_goodness_value_new = {
                k: max(postingsList_with_goodness_value_mini.get(k, 0), postingsList_with_goodness_value_global.get(k, 0)) for k in
                set(postingsList_with_goodness_value_mini) | set(postingsList_with_goodness_value_global)}

            postingsList_with_goodness_value_sorted_by_goodness = {k: v for k, v in sorted(postingsList_with_goodness_value_new.items(),
                                                                               key=lambda item: (-item[1], item[0]))}

            info_dict = {}
            info_dict["df"] = len(postingsList_with_goodness_value_sorted_by_goodness.keys())
            info_dict["postingsList_with_goodness_value"] = postingsList_with_goodness_value_sorted_by_goodness
            global_inverted_index_goodness[k] = info_dict

    global_inverted_index = {k: global_inverted_index_goodness[k] for k in sorted(global_inverted_index_goodness)}


    with open(r"../output/global_inverted_index_goodness.txt", "w", encoding=" utf−8") as output:
        for k, v in global_inverted_index.items():
            print("%-20s %-20s" % (k, v), file=output)
    print('\nMerged all mini inverted indices in all blocks to a global inverted index of goodness.')
    print('Global inverted index of goodness write out to file \"global_inverted_index_goodness.txt\"\n')

    return global_inverted_index