import sqlite3 
import json
import argparse
import os
from os import environ
from os.path import expanduser
def load_to_search_engine(type, file):
  json_data_file = open('./general.json')
  json_data = json.load(json_data_file)
  values_to_insert = []
  database_url = ''
  # if it is a linux platform
  if file:
    database_url = file
  else: 
    if os.name == 'posix':
      database_url = expanduser('~/.config/google-chrome/Default/Web Data')
    # if it is a windows platform. Noted! Don't know whether it actually works for windows
    elif os.name == 'nt':
      database_url = environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Default\Web Data'

  items = [x for x in json_data["links"] if x["type"] in type]
  print 'Items: ', items
  for item in items:
    values_to_insert.append((item["searchShortcut"], item["searchShortcut"], item["searchLink"],
                             item["searchLink"]))
  conn = sqlite3.connect(database_url)
  c = conn.cursor()

  # Multiple inserts into the database
  c.executemany("""INSERT INTO keywords('short_name','keyword', 'favicon_url', 'url')
                   VALUES (?,?,?,?)""", values_to_insert)

  conn.commit()
  conn.close()
  

parser = argparse.ArgumentParser(description='Modify the product speed')
# User can specify their project file directory, pre-generated file
parser.add_argument('--file', dest='file',
                    help='Indicate the file path of Web Data, if not we use default path')
parser.add_argument('--type', dest='type', default=[None], nargs='+',
                    help='Type of search engine settings you want. There is default and developer options')
parser.add_argument('--action', dest='action', required=True,
                    help='Type of action[Only load is useable atm]')
args = parser.parse_args()
if args.action == 'export':
  export_to_json()
if args.action == 'load':
  load_to_search_engine(args.type, args.file)

