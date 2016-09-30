# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
# from scrapy.selector import Selector
# from scrapy.utils.markup import remove_tags
# import lxml.html
# import lxml.etree
import html2text
import BeautifulSoup
import logging
import re


class IndeedPipeline(object):
    def process_item(self, item, spider):
        body = format_response(item)
        # if not text_inclusion(body):
        #     raise DropItem("Lacks mandatory text %s" % item)
        if text_exclusion(body):
            raise DropItem("Prohibited text %s" % item)
        return item


def format_response(item):
    body = item['link_response'].body
    body = remove_javascript(body)
    h = html2text.HTML2Text()
    h.ignore_links = True
    try:
        body = h.handle(body.decode('utf8'))
        body = body.lower()
    except Exception as oops:
        logging.warning("Html2text screwed up!!")
        logging.warning(oops.args)
    return body


def text_exclusion(body):
    anti_text = []
    anti_text.append(r"top secret")
    # anti_text.append(r"ts")
    # special characters don't play well with word boundaries...
    # anti_text.append(re.escape("c++"))
    for ii in anti_text:
        if re.search(r"\b" + ii + r"\b", body):
            return True
    return False


def text_inclusion(body):
    text = []
    #    text.append(r"ph")

    for ii in text:
        if re.search(r"\b" + ii + r"\b", body):
            return True
    return False

    # This should be done with lxml via elem.getparent().remove(elem), but
    # something fishy was going on with the getparent() function. Punt for now


def remove_javascript(link_response):
    soup = BeautifulSoup.BeautifulSoup(link_response)
    to_extract = soup.findAll('script')
    for ii in to_extract:
        ii.extract()
    return soup.prettify()

