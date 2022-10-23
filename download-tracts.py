import urllib.request
import ssl
import sqlite3
import zipfile
import os
import subprocess

#states = ['AZ', 'CA', 'CO', 'CT', 'FL', 'GA', 'HI', 'IL', 'IN', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN',
#          'MO', 'ME', 'MI', 'MN', 'MO', 'NC', 'NH', 'NJ', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'TN',
#          'TX', 'UT', 'VA', 'WA', 'WI']

wd = os.getcwd()
print(f'directory is {wd}')

db = sqlite3.connect('data/db/geodemo.db')
cur = db.cursor()

ssl._create_default_https_context = ssl._create_unverified_context

try:
    sql = 'select abbreviation, state_id from state'
    cur.execute(sql)
    data = cur.fetchall()

except sqlite3.Error as e:
    print(f'fatal error: {sql}')
    raise

for row in data:

    state = row[0]
    id = row[1]

    print(f'state: {state} id: {id}')

    #url = f'https://www.census.gov/cgi-bin/geo/shapefiles/getFile.php?year=2021&directory=TRACT&filename=tl_2021_{id:02}_tract.zip'
    url = f'https://www2.census.gov/geo/tiger/TIGER2021/TRACT/tl_2021_{id:02}_tract.zip'

    with urllib.request.urlopen(url) as f:
        data = f.read()
        dir = f'data/census/tracts/zip/{state}-tracts'
        zip = f'{dir}.zip'
        with open(zip, 'wb') as out:
            out.write(data)
            out.close()

            print(f'wrote file for {state}')

            with zipfile.ZipFile(zip, 'r') as zf:
                zf.extractall(dir)

            os.remove(zip)

            nd = f'{wd}/{dir}'
            print(f'changing directory to {nd}')
            os.chdir(nd)

            json = f'{wd}/data/census/tracts/{state}-tracts.json'
            print(f'running ogr on {json}')

            subprocess.run(['ogr2ogr', '-f', 'GeoJSON', json, f'tl_2021_{id:02}_tract.shp'])

            print(f'changing directory to {wd}')
            os.chdir(wd)





