import scrapy
import os
from bs4 import BeautifulSoup, Tag
import json
from scrapy.utils.project import get_project_settings

settings=get_project_settings()

class EverifyCrawlSpider(scrapy.Spider):
    name = 'everify_crawl'
    allowed_domains = ['e-verify.gov']
    start_urls = [
                    (
                        'http://e-verify.gov/'
                        'about-e-verify/e-verify-data/how-to-find-participating-employers?'
                        'field_account_status_value=All'
                        '&items_per_page=50'
                    )
                ]

    pagination_url = (
                        'http://e-verify.gov/'
                        'about-e-verify/e-verify-data/how-to-find-participating-employers?'
                        'field_account_status_value=All'
                        '&items_per_page=50'
                        '&viewsreference[data][title]=0'
                        '&viewsreference[enabled_settings][argument]=argument'
                        '&viewsreference[enabled_settings][title]=title&page='
                    )
    
    header = []

    total_records_count =  page_count = scraped_records_count = 0

    items_per_page = 50

    last_update = ''


    def parse(self, response):

        content = BeautifulSoup(response.body, 'html.parser')
        footer = content.find('footer').text
        left_string, right_string = 'of ', 'entries'
        self.total_records_count = int(footer[footer.index(left_string) + len(left_string) : footer.index(right_string)])
        table = content.find('table')

        # Extracting the table headers and defining it as keys
        thead = table.find('thead')
        if thead:
            for i, th in enumerate(thead.find_all('th')):
                self.header.append(th.text.strip().lower().replace(' ', '_'))
            header_file = settings.get('FILE_PATH_TO_EXTRACTED_FILES') + 'header.csv'
            self.save_to_file(header_file, ','.join(self.header))
        yield scrapy.Request(url=response.url, callback=self.scrap_page)


    def scrap_page(self, response):

        if response.status == 200:
            content = BeautifulSoup(response.body, 'html.parser')
            table = content.find('table')
            self.save_extracted_data_to_file(self.page_count, table)
            # data = self.process_content(content)
            # print(json.dumps(data, indent=4))

            self.scraped_records_count += self.items_per_page
            if self.scraped_records_count < self.total_records_count:
                self.page_count += 1
                yield scrapy.Request(url=self.pagination_url + str(self.page_count), callback=self.scrap_page)

    def save_extracted_data_to_file(self, page_number, tag):
        
        file_name = settings.get('FILE_PATH_TO_EXTRACTED_FILES') \
                    + 'Page ' \
                    + str(page_number) \
                    + settings.get('FILE_EXTENSION')

        self.save_to_file(file_name, str(tag))

    def save_to_file(self, file_name, data):
        f = open(file_name, 'w')
        f.write(data)
        f.close()


