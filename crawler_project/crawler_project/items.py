# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerProjectItem(scrapy.Item):
    # define the fields for your item here like:
    html_page = scrapy.Field()
    hyper_links = scrapy.Field()
    docID = scrapy.Field()
    url = scrapy.Field()
    docID_url_dict = scrapy.Field()
    goodness_of_url_dict = scrapy.Field()


