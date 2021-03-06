# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from crawlIndeed.items import IndeedItem
from scrapy.http import Request
import re


class Region:
    # Each region will have a url corresponding to each of 2 categories: software and traditional engineering.
    # This is basically a convenience class. The project began in a hackathon-like way and hasn't been properly
    # refined as of yet.
    def __init__(self, name):
        self.url_software = ""
        self.url_aeromech = ""
        self.name = name


class Indeed(scrapy.Spider):
    name = "indeed"
    allowed_domains = ["www.indeed.com"]

    software_base_url1 = "http://www.indeed.com/jobs?q=software+c%2B%2B&l="
    software_base_url2 = "&sr=directhire&radius=25&start="

    aeromech_base_url1 = "http://www.indeed.com/jobs?q=engineer+(mechanical+or+aerospace)&l="
    areomech_base_url2 = "&sr=directhire&radius=25&start="

    regions = []
    regions.append(Region("texas"))
    regions.append(Region("colorado"))
    regions.append(Region("washington+state"))
    regions.append(Region("massachusetts"))
    regions.append(Region("california"))
    regions.append(Region("washington+dc"))

    for state in regions:
        state.url_software = software_base_url1 + state.name + software_base_url2
        state.url_aeromech = aeromech_base_url1 + state.name + areomech_base_url2

    start_urls = []
    for state in regions:
        start_urls.append(state.url_software + "0")
        start_urls.append(state.url_aeromech + "0")

    # Each region seed will populate an n length list of follower pages.
    # parse() operates on an entry from start_urls
    def parse(self, response):
        depth = parse_page_max_depth(self, response)
        base_response_url = response.url
        base_response_url = base_response_url[:-1]
        for i in range(10, depth, 10):
            str1 = base_response_url + str(i)
            str1 = str1.decode('unicode-escape')
            yield scrapy.Request(str1, callback=self.parse_results_page)

    # Scrape useful info from target page and generate requests for follower links (handled in pipeline)
    def parse_results_page(self, response):
        sel = Selector(response)
        rows = sel.xpath('//div[@class="  row  result" or @class="lastRow  row  result"]')
        sponsored = sel.xpath('//div[@data-tn-section="sponsoredJobs"]')

        # Sponsored job listings have a different footprint
        for ii in sponsored:
            sub_rows = ii.xpath('div')
            for jj in sub_rows:
                item = IndeedItem()
                item['job_title'] = jj.xpath('a/@title').extract()
                item['company'] = jj.xpath('div/span[@class="company"]/text()').extract()
                if item['company'][0].isspace():
                    item['company'] = jj.xpath('div/span/a/text()').extract()

                item['location'] = jj.xpath('div/span[@class="location"]/text()').extract()
                item['date'] = jj.xpath('div/div/span[@class="date"]/text()').extract()
                item['link_url'] = jj.xpath('a/@href').extract()

                item = format_item(self, item)
                if not exclusion(self, item):
                    request = Request(item['link_url'], callback=self.parse_job_link)
                    request.meta['item'] = item
                    yield request

        # Gather normal job listings
        for ii in rows:
            item = IndeedItem()
            item['job_title'] = ii.xpath('h2/a/@title').extract()
            item['company'] = ii.xpath('span/span[@itemprop="name"]/text()').extract()
            if item['company'][0].isspace():
                item['company'] = ii.xpath('span/span/a/text()').extract()

            item['location'] = ii.xpath('span/span/span[@itemprop="addressLocality"]/text()').extract()
            item['date'] = ii.xpath('table/tr/td/div/div/span[@class="date"]/text()').extract()
            item['link_url'] = ii.xpath('h2/a/@href').extract()

            item = format_item(self, item)
            if not exclusion(self, item):
                request = Request(item['link_url'], callback=self.parse_job_link)
                request.meta['item'] = item
                yield request

    def parse_job_link(self, response):
        sel = Selector(response)
        item = response.request.meta['item']
        item['link_response'] = response
        return item


# Parse out the maximum result count so we can populate urls to that point
def parse_page_max_depth(self, response):
    sel = Selector(response)
    count = sel.xpath('//div[@id="searchCount"]/text()').extract()[0]
    search = re.search(r"Jobs \d+ to \d+ of ([\d,]+)", count)
    result_count = search.group(1)
    return int(result_count.replace(',', ''))


# Misc formatting for exclusion check. Pipeline would do this later anyhow.
def format_item(self, item):
    item['company'] = item['company'][0].lstrip('\n ')
    item['job_title'] = item['job_title'][0].lower()
    item['location'] = item['location'][0].lower()
    item['date'] = item['date'][0]
    item['link_url'] = 'http://www.indeed.com' + item['link_url'][0]
    return item


# Skipping here pares down the list of pages to be crawled, increasing speed non-trivially (vs in pipeline)
def exclusion(self, item):
    if date_exclusion(self, item):
        return True
    if job_title_exclusion(self, item):
        return True
    return False


def date_exclusion(self, item):
    if re.search(re.escape("30+"), item['date']):
        return True
    return False


def job_title_exclusion(self, item):
    anti_words = []
    anti_words.append(r"associate")
    anti_words.append(r"junior")
    anti_words.append(r"ruby")
    anti_words.append(r"manager")
    anti_words.append(r"building")
    anti_words.append(r"facilities")
    anti_words.append(r"field")
    anti_words.append(r"packaging")
    anti_words.append(r"intern")
    anti_words.append(r"quality")
    anti_words.append(r"electrical")
    anti_words.append(r"maintenance")
    anti_words.append(r"hvac")
    anti_words.append(r"reliability")
    anti_words.append(r"university")
    anti_words.append(r"technician")
    anti_words.append(r"business")
    anti_words.append(r"support")
    anti_words.append(r"co-op")
    anti_words.append(r"electrician")
    anti_words.append(r"cable")
    anti_words.append(r"student")
    anti_words.append(r"plant")
    anti_words.append(r"electronic")
    anti_words.append(r"civil")
    anti_words.append(r"drafter")
    anti_words.append(r"buyer")
    anti_words.append(r"sales")
    anti_words.append(r"hadoop")
    anti_words.append(r"cyber")
    anti_words.append(r"qa")
    anti_words.append(r"web")
    anti_words.append(r"vulnerability")
    anti_words.append(r"java")
    anti_words.append(r"manufacturing")

    for ii in anti_words:
        if re.search(r"\b" + ii + r"\b", item['job_title']):
            return True
    # special characters don't play well with word boundaries. for "C++", don't do \b
    # if re.search(re.escape("c++"), item["job_title"]):
    #     return True
    return False
