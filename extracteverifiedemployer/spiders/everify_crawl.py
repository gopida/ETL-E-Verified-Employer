import scrapy
from bs4 import BeautifulSoup
import json


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
    
    header = {}

    total_records_count =  page_count = scraped_records_count = 0

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
                self.header[i] = th.text.strip().lower().replace(' ', '_')

        yield scrapy.Request(url=response.url, callback=self.scrap_page)


    def scrap_page(self, response):
        if response.status == 200:
            content = BeautifulSoup(response.body, 'html.parser')
            data = self.process_content(content)
            # print(json.dumps(data, indent=4))
            ### save data ###

            self.scraped_records_count += len(data)
            print(self.scraped_records_count, self.total_records_count)
            if self.scraped_records_count < self.total_records_count:
                self.page_count += 1
                yield scrapy.Request(url=self.pagination_url + str(self.page_count), callback=self.scrap_page)



    def process_content(self, content):
        
        table = content.find('table')

        # Extracting the table rows/content/data
        data = []
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all("td")
            if self.header:
                items = {}
                for index in self.header:
                    items[self.header[index]] = cells[index].text.strip()
            else:
                items = []
                for index in cells:
                    items.append(index.text.strip())

            data.append(items)
        return data


