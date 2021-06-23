import scrapy

from ..items import CrawlerProjectItem
#from crawler_project.items import CrawlerProjectItem

class ConcordiaSpider(scrapy.Spider):
    name = 'concordia'
    allowed_domains = ['concordia.ca']
    start_urls = ['https://www.concordia.ca/']
    docID = 0
    visited_url_list = []
    #visited_url_list.append(start_urls[0])
    goodness_of_url_dict = {} #url: visited times
    #goodness_of_url_dict[start_urls[0]]=1

    docID_url_dict = {}

    upper_bound_total_number_of_pages = 2

    def parse(self, response):


        if response.url in self.visited_url_list:
            print('##############already visited, skip ######', response.url)

        else:
            if self.docID <self.upper_bound_total_number_of_pages:
                self.visited_url_list.append(response.url)
                self.docID = self.docID+1
                print('############## docID ######', self.docID, '############## url ######', response.url)
                print()
                self.docID_url_dict[self.docID] = response.url  # map docID to url

                item = CrawlerProjectItem()
                item['url'] = response.url
                item['html_page'] = response.body.decode()

                # if response.url not in self.visited_url_list:
                #     self.visited_url_list.append(response.url)

                #iterate over the URLs found in the page
                child_url_list = response.xpath('//a/@href').extract()
                full_child_url_list = []
                for url in child_url_list: #url type is str
                    url = response.urljoin(url)
                    if ('://' in url) and ('concordia.ca' in url) and (not url.endswith('.pdf') and (not url.endswith('.jpg')) and (url != response.url)):
                        full_child_url_list.append(url)

                for url in full_child_url_list: #url type is str
                    if url not in self.goodness_of_url_dict.keys():
                        self.goodness_of_url_dict[url] = 1
                    else:
                        updated_visited_times = self.goodness_of_url_dict[url] + 1
                        self.goodness_of_url_dict[url] = updated_visited_times

                    yield scrapy.Request(url, callback=self.parse)

                yield {
                    "docID": self.docID,
                    "docID_url_dict": self.docID_url_dict,
                    "goodness_of_url_dict": self.goodness_of_url_dict,
                    "url": response.url,
                    "html_page": response.body.decode()
                }