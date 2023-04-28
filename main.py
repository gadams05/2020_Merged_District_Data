import pandas as pd
import sqlite3
from state import state_abbreviations
from census import get_census_value
from pathlib import Path
import collections
import gzip
import json
import glob

path = 'data/db/geodemo.db'
Path(path).touch()
print('created db file')

db = sqlite3.connect(path)
cur = db.cursor()

tables = []
tables.append('''CREATE TABLE IF NOT EXISTS county(
        county_id integer not null,
        state_id integer not null,
        name text not null,
        total integer,
        white integer,
        black integer,
        native integer,
        asian integer,
        hawaaiin integer,
        other integer,
        latino integer,
        PRIMARY KEY (county_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS county_geo(
        county_id int not null,
        state_id int not null,
        coordinates text,
        PRIMARY KEY (county_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS state(
        state_id int not null,
        name text not null,
        abbreviation text not null,
        total int,
        white integer,
        black integer,
        native integer,
        asian integer,
        hawaaiin integer,
        other integer,
        latino integer,
        lat real not null,
        lng real not null,
        PRIMARY KEY (state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS district(
        district_id integer not null,
        state_id integer not null,
        name text not null,
        total integer,
        white integer,
        black integer,
        native integer,
        asian integer,
        hawaaiin integer,
        other integer,
        latino integer,
        PRIMARY KEY (district_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS district_geo(
        district_id int not null,
        state_id int not null,
        coordinates text,
        PRIMARY KEY (district_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS tract(
        tract_id real not null,
        county_id integer not null,
        state_id integer not null,
        name text not null,
        total integer,
        white integer,
        black integer,
        native integer,
        asian integer,
        hawaaiin integer,
        other integer,
        latino integer,
        PRIMARY KEY (tract_id, county_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS tract_geo(
        tract_id real not null,
        county_id int not null,
        state_id int not null,
        coordinates text,
        PRIMARY KEY (tract_id, county_id, state_id));''')

tables.append('''CREATE TABLE IF NOT EXISTS county_voting_2020(
        county_id int not null,
        state_id int not null,
        votes_gop int,
        votes_dem int,
        per_gop float,
        per_dem float,
        PRIMARY KEY (county_id, state_id)); ''')

tables.append('''CREATE TABLE IF NOT EXISTS district_voting_2020(
        district_id int not null,
        state_id int not null,
        votes_gop int,
        votes_dem int,
        per_gop float,
        per_dem float,
        PRIMARY KEY (district_id, state_id)); ''')

try:
    for table in tables:
        cur.execute(table)
        db.commit()

except sqlite3.OperationalError as e:
    print(f'duplicate table: {table}')

except sqlite3.Error as e:
    print(f'fatal error: {table}')
    db.commit()
    raise

print('created tables')

try:
    cur.execute('delete from county')
    cur.execute('delete from county_geo')
    cur.execute('delete from district')
    cur.execute('delete from district_geo')
    cur.execute('delete from state')
    cur.execute('delete from tract')
    cur.execute('delete from tract_geo')
    cur.execute('delete from county_voting_2020')
    cur.execute('delete from district_voting_2020')
    db.commit()

except sqlite3.Error as e:
    print(f'fatal error')
    db.commit()
    raise

print('deleted old data')

county_data = pd.read_csv(f'data/census/county.csv.gz', header=0, delimiter=',', compression='gzip')
state_data = pd.read_csv(f'data/census/state.csv.gz', header=0, delimiter=',', compression='gzip')
state_geo_data = pd.read_csv('data/census/state_geo.csv.gz', header=0, delimiter=',', compression='gzip')
geo_data = pd.read_csv('data/census/us-county-boundaries.csv.gz', index_col=0, header=0, delimiter=';', compression='gzip')
county_vote_data = pd.read_csv('data/census/county-vote2020.csv.gz', header=0, delimiter=',', compression='gzip')
district_data = pd.read_csv(f'data/census/district.csv.gz', header=0, delimiter=',', compression='gzip')
district_vote_data = pd.read_csv('data/census/district-vote2020.csv.gz', header=0, delimiter=',', compression='gzip')
tract_data = pd.read_csv(f'data/census/tract.csv.gz', header=0, delimiter=',', compression='gzip')

county_geo = {}

for index, row in geo_data.iterrows():

    state_ab = row['STUSAB']
    state = row['STATEFP']
    geo_id = row['GEOID']
    state_id = int(row['STATEFP'])
    county_id = int(row['COUNTYFP'])
    name = row['NAME']

    key = f'{state_id}-{county_id}'
    #print(f'{state_ab} {state} {name} {county_id}')
    county_geo[key] = row['Geo Shape']

    #print(f'added geo for {key}')

    #f'{{ "type": "Feature", "properties": {{ "name": "{name}", "color": "black" }}, "geometry": {json} }}'

counter = 0
for index, row in county_data.iterrows():
    geo_id = row['GEO_ID']
    state_id = int(geo_id[-5:-3])
    county_id = int(geo_id[-3:])
    name = row['NAME'].split(',')[0]

    total = get_census_value('total', row)
    white = get_census_value('white', row)
    black = get_census_value('black', row)
    native = get_census_value('native', row)
    asian = get_census_value('asian', row)
    hawaiian = get_census_value('hawaiian', row)
    other = get_census_value('other', row)
    latino = get_census_value('latino', row)

    try:
        sql = f'''INSERT INTO county VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data = (county_id, state_id, name, total, white, black, native, asian, hawaiian, other, latino)
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {sql}')
        db.commit()
        raise

print(f'wrote {counter} counties')
counter = 0

for index, row in district_data.iterrows():
    geo_id = row['GEO_ID']
    state_id = int(geo_id[-4:-2])
    district_id = geo_id[-2:]
    if district_id == 'ZZ':
        district_id = 0
    else:
        district_id = int(district_id)

    name = row['NAME'].split(',')[0]

    total = get_census_value('total', row)
    white = get_census_value('white', row)
    black = get_census_value('black', row)
    native = get_census_value('native', row)
    asian = get_census_value('asian', row)
    hawaiian = get_census_value('hawaiian', row)
    other = get_census_value('other', row)
    latino = get_census_value('latino', row)

    try:
        sql = f'''INSERT INTO district VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data = (district_id, state_id, name, total, white, black, native, asian, hawaiian, other, latino)
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {sql}')
        db.commit()
        raise

print(f'wrote {counter} districts')
counter = 0

with gzip.open('data/census/districts-116.json.gz', 'r') as fin:
    json_bytes = fin.read()

json_str = json_bytes.decode('utf-8')
data = json.loads(json_str)

counter = 0

for feature in data['features']:
    props = feature['properties']
    geo_id = props['GEOID']
    district_id = geo_id[-2:]
    if district_id == 'ZZ':
        district_id = 0
    else:
        district_id = int(district_id)

    state_id = int(props['STATEFP'])
    coordinates = str(feature['geometry']).replace("'", "\"")

    #print(f'geo: {geo_id} state: {state_id} district: {district_id}')

    try:
        sql = f'''INSERT INTO district_geo VALUES(?, ?, ?)'''
        data = (district_id, state_id, coordinates)
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {sql} {data}')
        db.commit()
        raise

print(f'wrote {counter} district geos')
counter = 0

for index, row in tract_data.iterrows():
    geo_id = row['GEO_ID']
    state_id = int(geo_id[9:11])
    county_id = int(geo_id[11:14])
    tract_base = int(geo_id[14:18])
    tract_fraction = int(geo_id[18:])

    if tract_fraction > 0:
        tract_id = tract_base + (tract_fraction / 100)
    else:
        tract_id = tract_base
    name = row['NAME'].split(',')[0]

    total = get_census_value('total', row)
    white = get_census_value('white', row)
    black = get_census_value('black', row)
    native = get_census_value('native', row)
    asian = get_census_value('asian', row)
    hawaiian = get_census_value('hawaiian', row)
    other = get_census_value('other', row)
    latino = get_census_value('latino', row)

    #print(f'tract: tract: {tract_id} county: {county_id} state: {state_id}')

    try:
        sql = f'''INSERT INTO tract VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        data = (tract_id, county_id, state_id, name, total, white, black, native, asian, hawaiian, other, latino)
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {sql}')
        db.commit()
        raise

print(f'wrote {counter} tracts')
counter = 0

for file in glob.glob('data/census/tracts/*.gz'):

    print(f'opening tract file {file}');

    with gzip.open(file, 'r') as fin:
        json_bytes = fin.read()

    json_str = json_bytes.decode('utf-8')
    data = json.loads(json_str)

    for feature in data['features']:
        props = feature['properties']
        geo_id = props['GEOID']
        state_id = int(geo_id[:2])
        county_id = int(geo_id[2:5])
        tract_base = int(geo_id[5:9])
        tract_fraction = int(geo_id[9:])
        if tract_fraction > 0:
            tract_id = tract_base + (tract_fraction / 100)
        else:
            tract_id = tract_base
        coordinates = str(feature['geometry']).replace("'", "\"")

        #print(f'geo: {geo_id} state: {state_id} tract: {tract_id}')

        try:
            sql = f'''INSERT INTO tract_geo VALUES(?, ?, ?, ?)'''
            data = (tract_id, county_id, state_id, coordinates)
            cur.execute(sql, data)
            db.commit()
            counter = counter + 1

        except sqlite3.IntegrityError as e:
            print(f'duplicate row: {sql}')

        except sqlite3.Error as e:
            print(f'fatal error: {sql} {data}')
            db.commit()
            raise

print(f'wrote {counter} tract geos')
counter = 0

state_geo = collections.defaultdict(dict)
state_ids = collections.defaultdict(dict)

for index, row in state_geo_data.iterrows():

    state = row['STATE']
    lat = row['LATITUDE']
    lng = row['LONGITUDE']

    state_geo[state]['lat'] = lat
    state_geo[state]['lng'] = lng

for index, row in state_data.iterrows():

    geo_id = row['GEO_ID']
    name = row['NAME']
    state_id = int(geo_id[-2:])
    total = get_census_value('total', row)
    white = get_census_value('white', row)
    black = get_census_value('black', row)
    native = get_census_value('native', row)
    asian = get_census_value('asian', row)
    hawaiian = get_census_value('hawaiian', row)
    other = get_census_value('other', row)
    latino = get_census_value('latino', row)

    if name in state_abbreviations:
        abbrev = state_abbreviations[name]

        state_ids[abbrev] = state_id

        if abbrev in state_geo:

            lat = state_geo[abbrev]['lat']
            lng = state_geo[abbrev]['lng']

            try:
                sql = f'''INSERT INTO state VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                data = (state_id, name, abbrev, total, white, black, native, asian, hawaiian, other, latino, lat, lng)
                cur.execute(sql, data)
                db.commit()
                counter = counter + 1

            except sqlite3.IntegrityError as e:
                print(f'duplicate row: {e} {sql}')

            except sqlite3.Error as e:
                print(f'fatal error: {e} {sql}')
                db.commit()
                raise
        else:
            print(f'failed to find coorindates for {name}')

    else:
        print(f'failed to find abbrevation for {name}')

print(f'wrote {counter} states')
counter = 0

for index, row in county_data.iterrows():

    geo_id = row['GEO_ID']
    state_id = int(geo_id[-5:-3])
    county_id = int(geo_id[-3:])

    key = f'{state_id}-{county_id}'

    if key in county_geo:
        #coordinates = county_geo[county_id].translate(str.maketrans({'"': r'\"'}))
        coordinates = county_geo[key]
        try:
            sql = f'''INSERT INTO county_geo VALUES(?, ?, ?)'''
            data = (county_id, state_id, coordinates)
            cur.execute(sql, data)
            db.commit()
            counter = counter + 1

        except sqlite3.IntegrityError as e:
            print(f'duplicate row: {e} {sql}')

        except sqlite3.Error as e:
            print(f'fatal error: {e} {sql}')
            db.commit()
            raise
    else:
        print(f'failed to find coordinates for {key}')

print(f'wrote {counter} geos')
counter = 0

for index, row in county_vote_data.iterrows():
    fips = row['county_fips']
    county_id = str(fips)[-3:]
    state_id = str(fips)[:-3]

    try:
        sql = f'''INSERT INTO county_voting_2020 VALUES(?, ?, ?, ?, ?, ?)'''
        data = (county_id, state_id, row['votes_gop'], row['votes_dem'], row['per_gop'], row['per_dem'])
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {e} {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {e} {sql}')
        db.commit()
        raise

print(f'wrote {counter} county votes')
counter = 0

for index, row in district_vote_data.iterrows():

    district = row['District']
    district_id = district[-2:]
    state = district[:2]

    if district_id == 'AL':
        district_id = 0

    if state not in state_ids:
        print(f'No state for {state}')
        continue

    state_id = state_ids[state]

    try:
        sql = f'''INSERT INTO district_voting_2020 VALUES(?, ?, ?, ?, ?, ?)'''
        data = (district_id, state_id, row['Trump'], row['Biden'], row['Trump%'], row['Biden%'])
        cur.execute(sql, data)
        db.commit()
        counter = counter + 1

    except sqlite3.IntegrityError as e:
        print(f'duplicate row: {e} {sql}')

    except sqlite3.Error as e:
        print(f'fatal error: {e} {sql}')
        db.commit()
        raise

print(f'wrote {counter} district votes')
counter = 0
