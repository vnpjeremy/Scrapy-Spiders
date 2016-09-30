import scrapy


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

    start_urls = []

    def parse(self, response):
        pass

    def parse_results_page(self, response):
        pass
