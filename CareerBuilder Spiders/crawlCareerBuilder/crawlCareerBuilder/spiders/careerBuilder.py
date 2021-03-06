import scrapy
from scrapy.selector import Selector
from crawlCareerBuilder.items import CareerBuilderItem
from scrapy.http import Request
import re


class Region:
    def __init__(self, name):
        self.url_software = ""
        self.url_aeromech = ""
        self.name = name


# Careerbuilder is awful right now and doesn't allow OR operations with search critera, so just populate 'engineer'
# search seed pages for now. Use scrapy framework to filter appropriately. It looks like it only shows 2500 results
# for a single search, and manually altering the URL doesn't allow for further querying.
class CareerBuilder(scrapy.Spider):
    name = "careerBuilder"
    allowed_domains = ["www.careerbuilder.com"]

    software_base_url1 = "http://www.careerbuilder.com/jobs-software-in-"
    software_base_url2 = "?page_number="

    regions = []
    regions.append(Region("dallas-fort-worth,tx"))

    for state in regions:
        state.url_software = software_base_url1 + state.name + software_base_url2

    start_urls = []
    for state in regions:
        start_urls.append(state.url_software + "0")

    # Note: for the careerbuilder site, page 0 and 1 will be identical
    def parse(self, response):
        depth = parse_page_max_depth(self, response)
        base_response_url = response.url
        base_response_url = base_response_url[:-1]
        pages = depth / 25
        for i in range(1, pages, 1):
            str1 = base_response_url + str(i)
            str1 = str1.decode('unicode-escape')
            yield scrapy.Request(str1, callback=self.parse_results_page)

    def parse_results_page(self, response):
        sel = Selector(response)
        job_rows = sel.xpath('//div[@class="job-row"]')
        for row in job_rows:
            item = CareerBuilderItem()
            job_title = row.xpath('div/div/h2/a[@href]/text()').extract()
            company = row.xpath('div/div/h4/a[@href]/text()').extract()
            location = row.xpath('div/div/h4[@class="job-text"]/text()').extract()
            arg = 4


def parse_page_max_depth(self, response):
    sel = Selector(response)
    count = sel.xpath('//div[@class="count"]/text()').extract()[0]
    search = re.findall(r'\d+', count)
    return int(search[0])
