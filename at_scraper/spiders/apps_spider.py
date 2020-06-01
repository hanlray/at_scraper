import scrapy
import logging
from bs4 import BeautifulSoup
from at_scraper.items import AppItem, AltItem, SoftwareDetailsItem

class AppsSpider(scrapy.Spider):
    name = "apps"
    start_urls = [
        'https://alternativeto.net/platform/all/?p=1',
    ]

    def parse(self, response):
        #logging.debug(response.url + ' returned')
        for item in response.css('ul li.app-list-item'):
            href = item.css('.app-header a').attrib['href']
            yield scrapy.Request(url=response.urljoin(href), callback=self.parse_app)

        next_page = response.css('.pagination span.next').get()
        if next_page is not None:
            urlArr = response.url.rsplit("=", 1)
            nextPageNumber = str(int(urlArr[1]) + 1)
            next_page = urlArr[0] + '=' + nextPageNumber
            yield scrapy.Request(next_page, callback=self.parse)
            

    def get_slug(self, href):
        a = href.rsplit('/', 3)
        if(a[-2] == 'about'): return a[-3]
        return a[-2]

    def get_name(self, response):
        name = response.css('#appHeader h1::text').get()
        if(name is not None): return name

        title = response.css('.bluebox-body h1::text').get()
        return title[0:title.find('Alternatives and Similar Software')]

    def process_target_part(self, target, response):
        name = self.get_name(response)

        lead = response.css('#appHeader p.lead::text').get()

        creatorLink = response.css('#appHeader .creator a::attr(href)').get()
        #if(bool(creatorAttrib)): creatorLink = creatorAttrib['href']

        website = response.css('a.icon-official-website::attr(href)').get()
        #if(bool(websiteAttrib)): website = websiteAttrib['href'] 

        desc = []
        for p in response.css('.item-desc p'):
            desc.append(BeautifulSoup(p.get(), "lxml").text)
        description = '\n'.join(desc)
        if not description: description = None
        logging.debug('scraped description for ' + target + ':' + description)

        return SoftwareDetailsItem(
            slug=target,
            name=name,
            creator_link=creatorLink,
            lead=lead,
            website=website,
            description=description
        )

    def parse_app(self, response):
        target = response.url.rsplit('/', 2)[-2]

        yield self.process_target_part(target, response)

        for idx, app_item in enumerate(response.css('ul#alternativeList > li')):
            attrib = app_item.css('h3 a').attrib
            if(not bool(attrib)): continue
            href = attrib['href']
            name = app_item.css('h3 a::text').get()
            yield AltItem(
                alt_to=target, 
                slug=self.get_slug(href),
                name=name,
                desc_primary=app_item.css('p.text::text').get(),
                rank=idx+1,
            )