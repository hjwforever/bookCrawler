# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import datetime

import pymysql
from bookCrawler import settings


# 数据存储在csv文件里
class ScrapyBookPipeline(object):
    def __init__(self):
        # 连接数据库
        self.db = pymysql.Connect(
            host=settings.MYSQL_HOST,
            database=settings.MYSQL_DB_NAME,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8',
        )

        # 创建游标对象
        self.cur = self.db.cursor()

        # 打开csv文件
        self.file = open('data.csv', 'w', newline='', encoding='utf-8')
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(['书名', '作者', '出版社', '出版时间', '价格', '页数', '简介', '类别', '小图标', '大图标'])

    def process_item(self, item, spider):
        # 查询数据表数据
        if item['scrible'] is None:
            return item
        categories = item['category'].split(">")
        print("category", categories)

        parent_id = -1
        for indx, category in enumerate(categories):
            sql = " select * from book_category where name = '%s' " % category
            self.cur.execute(sql)
            data = self.cur.fetchone()

            if data is None:
                create_category_sql = "insert into book_category values(%s,%s,%s,%s,%s,%s,%s,%s);" % (
                "NULL", parent_id, '"' + str(category) + '"', 1, 1, 1 if indx < len(categories) - 1 else 0,
                datetime.date.today(), datetime.date.today())
                self.cur.execute(create_category_sql)
                res = self.cur.fetchone()
                print("插入:", res)
                parent_id = res[0]

            else:
                parent_id = data[0]

        self.db.commit()
        self.csvwriter.writerow(
            [item["title"], item["author"], item["publisher"], item["pub_date"], item["price"], item["pages"],
             item["scrible"], item["category"], item["s_img"], item["b_img"]])
        return item

    def close_spider(self, spider):
        self.file.close()
        self.cur.close()
        self.db.close()
