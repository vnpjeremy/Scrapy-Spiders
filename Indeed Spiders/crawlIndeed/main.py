from scrapy import cmdline
import os

file = "indeedScrapyOutput.csv"
cmd = "scrapy crawl indeed -o "
both = cmd + file
if os.path.isfile(file):
    os.remove(file)
cmdline.execute(both.split())
