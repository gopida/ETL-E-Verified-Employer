from scrapy.utils.project import get_project_settings
from glob import glob
import json
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

settings=get_project_settings()

file_path_to_json = settings.get('FILE_PATH_TO_TRANSFORMED_FILES') + '*.json'
files_to_load = glob(file_path_to_json)

#Connecting to cloud mongodb
client = pymongo.MongoClient(os.getenv('mongodbconnection'))
db = client.everifydb #database name
collection = db.employers #table/collection name

#read transformed file and inject in database
for data_file in files_to_load:
    json_data = json.load(open(data_file,'r'))
    collection.insert_many(json_data)

print('Success')