# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
import os

class CrawlerProjectPipeline:
    # def open_spider(self, spider):
    #     print('begin')

    def process_item(self, item, spider):
        # save the whole html pages out to file

        with open(r"../output/html_files/" + str(item['docID'])  +".html", "w", encoding="utf-8") as file:
            file.write(item['html_page'])
        # save the docID_url_dict out to file, mapping the docID to url of the html page
        json.dump(item['docID_url_dict'], open(r'../output/html_files/docID_url_dict' + ".json", "w", encoding=" utf−8"), indent=3)
        json.dump(item['goodness_of_url_dict'], open(r'../output/html_files/goodness_of_url_dict' + ".json", "w", encoding=" utf−8"), indent=3)
        return item

    # def close_spider(self, spider):
    #     print('')