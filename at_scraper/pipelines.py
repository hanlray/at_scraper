# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
from mysql.connector import errorcode
import logging
from at_scraper.items import AppItem, AltItem, SoftwareDetailsItem

class AtScraperPipeline:
    def __init__(self, mysql_user, mysql_password, mysql_database):
        self.user = mysql_user
        self.password = mysql_password
        self.database = mysql_database

    def process_item(self, item, spider):
        #logging.debug('Processing an item')
        if isinstance(item, AltItem):
            return self.handleAltItem(item, spider)
        if isinstance(item, AppItem):
            return self.handleAppItem(item, spider)
        if isinstance(item, SoftwareDetailsItem):
            return self.handleSoftwareDetailsItem(item, spider)
        
    def handleAltItem(self, item, spider):
        #logging.debug('Handling an AltItem')
        cursor = self.cnx.cursor()
        query = ("SELECT id FROM software "
                 "WHERE slug = %s")
        cursor.execute(query, (item['alt_to'],))
        row = cursor.fetchone()
        app_id = row[0]
        alt_id = self.save_app(cursor, item)

        self.saveAlt(cursor, app_id, alt_id, item['rank'])
        self.cnx.commit()
        cursor.close()

        return item

    def saveAlt(self, cursor, to_id, alt_id, rank):
        query = ("INSERT INTO alternative "
                 "(to_id, alt_id, rank_atnet) "
                 "VALUES (%s, %s, %s) "
                 "ON DUPLICATE KEY UPDATE rank_atnet=%s")
        cursor.execute(query, (to_id, alt_id, rank, rank))

    # save app and get its id
    def save_app(self, cursor, app):
        save_app = ("INSERT INTO software "
                   "(slug, name) "
                   "VALUES (%s, %s) "
                   "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)")

        cursor.execute(save_app, (app['slug'], app['name']))
        return cursor.lastrowid

    def handleSoftwareDetailsItem(self, item, spider):
        cursor = self.cnx.cursor()

        sql = ("INSERT INTO software "
                "(slug, name, lead, description, creator_link, website) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
                "ON DUPLICATE KEY UPDATE description=%s")

        cursor.execute(sql, (item['slug'], item['name'], item['lead'], item['description'], item['creator_link'], item['website'], item['description']))

        self.cnx.commit()
        cursor.close()

    def handleAppItem(self, item, spider):
        cursor = self.cnx.cursor()
        add_app = ("INSERT INTO software "
                   "(slug, title, desc_primary) "
                   "VALUES (%s, %s, %s)"
                   "ON DUPLICATE KEY UPDATE desc_primary=%s")

        cursor.execute(add_app, (item['slug'], item['name'], item['desc_primary'], item['desc_primary']))
        self.cnx.commit()
        cursor.close()

        return item


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_database=crawler.settings.get('MYSQL_DATABASE')
        )

    def open_spider(self, spider):
        try:
            logging.debug('Connecting to mysql')
            self.cnx = mysql.connector.connect(
                user=self.user, password=self.password, database=self.database)
            logging.debug('Connected to mysql')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def close_spider(self, spider):
        self.cnx.close()
