import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

url = "https://main.sci.gov.in/php/v_judgments/getJBJ.php"


def save_metadata(record):
    file_name = "metadata/" + str(record['Id']) + ".json"
    with open(file_name, 'w') as outfile:
        json.dump(record, outfile)


def save_data(record):
    if 'Judgment link' in record:
        pdf_file = Path("data/" + str(record['Id']) + ".pdf")
        url = record['Judgment link']
        response = requests.get(url, verify=False)
        pdf_file.write_bytes(response.content)


def getData(year):
    payload = {
        'JBJfrom_date': '01-01-' + year,
        'JBJto_date': '31-12-' + year,
        'jorrop': 'J',
        'ansCaptcha': '1452'
    }

    response = requests.request("POST", url, verify=False, data=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find_all('table')[0]
    ##data = []
    headers = [
        'Diary Number', 'Case Number', 'Petitioner Name', 'Respondent Name',
        'Petitioner\'s Advocate', 'Respondent\'s Advocate', 'Bench',
        'Judgment By', 'Judgment link'
    ]
    startindex = 1
    record = dict()
    judgment_links = []
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 1:
            # collected a whole record so save it
            if len(judgment_links):
                for link in judgment_links:
                    record['Judgment link'] = link['Judgment link']
                    record['Judgement Date'] = link['Judgement Date']
                    record['Id'] = year + "_" + str(startindex)
                    save_metadata(record)
                    save_data(record)
                    startindex = startindex + 1
                    print('......' + str(startindex) + '.......')
            else:
                record['Judgment link'] = None
                record['Judgement Date'] = None
                record['Id'] = year + "_" + str(startindex)
                save_metadata(record)
                save_data(record)
                startindex = startindex + 1
                #data.append(record)
            record = dict()
            judgment_links = []
        state = None
        for column in columns:
            if state == 'Judgment link':
                a_blocks = column.find_all('a')
                for a in a_blocks:
                    if a.text.strip():  # remove empty blocks
                        ldata = {}
                        ldata[
                            'Judgment link'] = 'https://main.sci.gov.in' + a.get(
                                'href')
                        ldata['Judgement Date'] = a.text.strip()[:10]
                        judgment_links.append(ldata)
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
    #with open('data/'+year+'.json', 'w') as outfile:
    #  json.dump(data, outfile)


# for i in range (1980,1949,-1):
#   print("Getting data for "+str(i))
#   getData(str(i))
getData(str(2019))
