import sqlite3 
import json
import argparse
import os
from os import environ
from os.path import expanduser

# Get path to the browser data depending on the browser type
def get_path_to_browser_data(path):
 # if it is a linux platform
  if path:
    return path 
  else: 
    if os.name == 'posix':
      return expanduser('~/.config/google-chrome/Default/Web Data')
    # if it is a windows platform. Noted! Don't know whether it actually works for windows
    elif os.name == 'nt':
      return environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Default\Web Data'

def load_to_search_engine(type, path):
  json_data_file = open('./general.json')
  json_data = json.load(json_data_file)
  values_to_insert = []
  database_url = get_path_to_browser_data(path)
  # if it is a linux platform
  items = [x for x in json_data["links"] if x["type"] in type]
  for item in items:
    values_to_insert.append((item["searchShortcut"], item["searchShortcut"], item["searchLink"],
                             item["searchLink"], item['searchShortcut'])) 
  conn = sqlite3.connect(database_url)
  c = conn.cursor()
  # Begin transaction
  c.execute('begin transaction;')
  for item in values_to_insert:
    # Insert into DB if keyword does not exist in chrome keywords table 
    c.execute('INSERT INTO keywords("short_name", "keyword", "favicon_url", "url") SELECT ?,?,?,? WHERE NOT EXISTS (SELECT keyword from keywords WHERE keyword=?);', item) 
  # Multiple inserts into the database
  rows =  c.rowcount
  # Commit sql statements
  conn.commit()
  conn.close()

def export_to_json(path):
  database_url = get_path_to_browser_data(path)
  conn = sqlite3.connect(database_url)
  c = conn.cursor()
  c.execute('SELECT short_name, keyword, favicon_url, url FROM keywords')
  rows = c.fetchall()
  dict_list = []
  columns = ['short_name', 'keyword', 'favicon_url', 'url']
  for row in rows:
    zipped = zip(columns, row)  
    dict_list.append(dict((x, y) for x, y in zipped))
  print dict_list 
  # Writing json data
  with open('./data.json', 'w') as f:
    json.dumps({'links': dict_list}, f, indent=4)
  conn.close()

def import_json(browser_path, json_path):
  database_url = get_path_to_browser_data(browser_path)
  # Load json file
  with open(json_path) as json_data:
    search_data = json.load(json_data)
  print search_data
  items = [x for x in search_data["links"]]
  values_to_insert = []
  for item in items:
    values_to_insert.append((item["searchShortcut"], item["searchShortcut"], item["searchLink"],
                             item["searchLink"], item['searchShortcut'])) 
  conn = sqlite3.connect(database_url)
  c = conn.cursor()
  # Begin transaction
  c.execute('begin transaction;')
  for item in values_to_insert:
    # Insert into DB if keyword does not exist in chrome keywords table 
    c.execute('INSERT INTO keywords("short_name", "keyword", "favicon_url", "url") SELECT ?,?,?,? WHERE NOT EXISTS (SELECT keyword from keywords WHERE keyword=?);', item) 
  # Multiple inserts into the database
  rows =  c.rowcount
  # Commit sql statements
  conn.commit()
  conn.close()

parser = argparse.ArgumentParser(description='Modify the product speed')
# User can specify their project file directory, pre-generated file
parser.add_argument('--browser_path', dest='browser_path',
                    help='Indicate the file path of Web Data, if not we use default path')
parser.add_argument('--json', dest='json_path',
                    help='Json file which you want to import the setting')
parser.add_argument('--type', dest='type', default=[None], nargs='+',
                    help='Type of search engine settings you want. There is default and developer options')
parser.add_argument('--action', dest='action', required=True,
                    help='Type of action[Only load is useable atm]')
parser.add_argument('--file', dest='file', default=[None], nargs='+',
                    help='JSON file to import')
args = parser.parse_args()
if args.action == 'import':
  import_json(args.browser_path, args.json_path)
if args.action == 'export':
  export_to_json(args.browser_path)
if args.action == 'load':
  load_to_search_engine(args.type, args.browser_path)
