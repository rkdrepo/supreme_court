import requests
from bs4 import BeautifulSoup
import json

url = "https://main.sci.gov.in/php/v_judgments/getJBJ.php"

def getData(year):
  payload = {'JBJfrom_date': '01-01-'+year,
  'JBJto_date': '31-12-'+year,
  'jorrop': 'J',
  'ansCaptcha': '1452'}

  response = requests.request("POST", url, verify=False,  data = payload)
  soup = BeautifulSoup(response.text, 'lxml')
  table = soup.find_all('table')[0]
  data = []
  headers = ['Diary Number','Case Number','Petitioner Name','Respondent Name', 'Petitioner\'s Advocate', 'Respondent\'s Advocate', 'Bench', 'Judgment By', 'Judgment link']

  record = dict()
  for row in table.find_all('tr'):
      columns = row.find_all('td')
      if len(columns) == 1:
        data.append(record)
        record = dict()
      state = None
      for column in columns:
        if state == 'Judgment link':
          text = 'https://main.sci.gov.in/' + column.a['href']
        else:
          text = column.text
        if text:
          if state in headers:
            record[state] = text
            if state == 'Case Number':
              state = 'Judgment link'
            else:
              state = None
          else:
            state = text

  #print(data)
  with open('data/'+year+'.json', 'w') as outfile:
    json.dump(data, outfile)

for i in range (1980,1949,-1):
  print("Getting data for "+str(i))
  getData(str(i))
