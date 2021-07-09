# -*- coding: utf-8 -*-
import scrapy
import json

from bookCrawler.items import ScrapyBookItem


class SpiderForXPath(scrapy.Spider):
    name = 'spider_xinhua'

    def start_requests(self):
        for a in range(1, 2):
            url = 'https://search.xhsd.com/search?frontCategoryId=41&pageNo={}'.format(a)
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        items = []
        for book in response.xpath('//ul[@class="shop-search-items-img-type"]/li'):
            item = ScrapyBookItem()

            title1 = book.xpath("./p[1]/a/text()").extract_first().replace('\n', '').strip()
            # title2 = "无" if book.xpath("./tr/td[2]/div[1]/span/text()").extract_first() == None else book.xpath(
            #     "./tr/td[2]/div[1]/span/text()").extract_first().replace('\n', '').strip()
            # item['title'] = title1 + "(" + title2 + ")"
            item['title'] = title1
            item['author'] = "" if book.xpath("./p[2]/span/text()").extract_first() is None else book.xpath("./p[2]/span/text()").extract_first().replace('\n', '').strip()
            item['s_img'] = "https:" + book.xpath("./div[1]/a/img/@src").extract_first().replace('\n', '').strip()
            item['price'] = book.xpath("./p[3]/span/text()").extract_first().replace('\n', '').strip()
            # item['scrible'] = "无" if book.xpath("./tr/td[2]/p[2]/span/text()").extract_first() == None else book.xpath(
            #     "./tr/td[2]/p[2]/span/text()").extract_first().replace('\n', '').strip()
            sub_url = book.xpath("./div[1]/a/@href").extract_first().replace('\n', '').strip()
            sub_url ="https:" + sub_url
            items.append(item)

            # meta={"item":item} 传递item引用SinaItem对象
            yield scrapy.Request(url=sub_url, callback=self.parse_second, meta={"item": item})

    def parse_second(self, response):
        item = response.meta["item"]
        item["category_id"] = ""
        item['pub_date'] = ""
        item['pages'] = ""

        category = ""
        # 爬取分类
        for classification in response.xpath('//ol[@class="breadcrumb"]/li'):
            if len(classification.xpath("./a/text()")):
                category += classification.xpath("./a/text()").extract_first().replace('\n', '').strip()
                category += ">"
        item["category"] = category[:-1]

        # 爬取出版社
        item["publisher"] = response.xpath('//div[@class="item-title"]/label[1]/a/text()').extract_first().replace('\n', '').strip()

        # 爬取大图
        item["b_img"] = "https:" + response.xpath('//img[@class="js-main-image"]/@src').extract_first().replace('\n', '').strip()

        # 爬取描述
        detail = response.xpath('//div[@class="spu-tab-item-detail"]/@data-detail').extract_first().replace('\n', '').strip()
        if detail != '[]':
            scrible = json.loads(detail)
            item['scrible'] = scrible[0]["content"].replace('&nbsp;', '').replace('<p>', '').replace('</p>', '').replace('&ldquo;', '“').replace('&rdquo;', '”').replace('&mdash;', '—').replace('&hellip;', '...').strip()
        else:
            item['scrible'] = ""

        # 爬取ISBN
        print("ISBN***************************************************************")
        print(response.xpath('//div[@class="spu-info"]/ul/li[1]/span[2]/text()').extract_first().replace('\n', '').strip())

        # 爬取发布时间
        print("首发时间***************************************************************")
        print(response.xpath('//div[@class="spu-info"]/ul/li[14]/span[2]/text()').extract_first().replace('\n', '').strip())
        for msg in response.xpath('//div[@class="spu-info"]/ul/li'):
            if msg.xpath("./span[1]/text()").extract_first() is not None and msg.xpath("./span[1]/text()").extract_first().replace('\n', '').strip() == "首版时间":
                item['pub_date'] = msg.xpath("./span[2]/text()").extract_first().replace('\n', '').strip()
            elif msg.xpath("./span[1]/text()").extract_first() is not None and msg.xpath("./span[1]/text()").extract_first().replace('\n', '').strip() == "页数":
                item['pages'] = msg.xpath("./span[2]/text()").extract_first().replace('\n', '').strip()

        # book = response.xpath('//div[@class="indent"]/div').extract_first()
        # item["pub_date"] = book.xpath("./div[1]/a/@href").extract_first().replace('\n', '').strip()
        # item["m_img"] = book.xpath("./div[1]/a/@href").extract_first().replace('\n', '').strip()
        # item["isbn"] = book.xpath("./div[2]/a[1]/text()").extract_first().replace('\n', '').strip()
        yield item
