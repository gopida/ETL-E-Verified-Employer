from pathlib import Path
import os
from bs4 import BeautifulSoup, Tag
import json
from scrapy.utils.project import get_project_settings

settings=get_project_settings()

class Transform():


    header_file = settings.get('FILE_PATH_TO_EXTRACTED_FILES') + 'header.csv'
    f = open(header_file, 'r')
    headers = {}
    for i, header in enumerate(f.read().split(',')):
        headers[i] = header

    def process_content_to_json(self, content):
    
        table = content.find('table')

        # Extracting the table rows/content/data
        data = []
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all("td")
            if self.header:
                items = {}
                for index in self.headers:
                    items[self.headers[index]] = cells[index].text.strip()
            else:
                items = []
                for index in cells:
                    items.append(index.text.strip())

            data.append(items)
        return data


    def get_files_and_transform(self):
        for htmlfile in Path(settings.get('FILE_PATH_TO_EXTRACTED_FILES')).glob('*' + settings.get('FILE_EXTENSION')):
            content = BeautifulSoup(htmlfile.read_text(), 'html.parser')
            data = self.process_content_to_json(content)
            file_name = settings.get('FILE_PATH_TO_TRANSFORMED_FILES') + htmlfile.stem + '.json'
            self.save_to_file(file_name, json.dumps(data, indent=4))

    def save_to_file(self, file_name, data):
            f = open(file_name, 'w')
            f.write(data)
            f.close()

t = Transform()
t.get_files_and_transform()
