from scrapy import cmdline
import os

file = "careerBuilderScrapyOutput.csv"
cmd = "scrapy crawl careerBuilder -o "
both = cmd + file
if os.path.isfile(file):
    os.remove(file)
cmdline.execute(both.split())
