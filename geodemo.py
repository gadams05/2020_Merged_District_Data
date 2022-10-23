import pandas as pd
import geojson

api_key='YOUR_GOOGLE_MAPS_API_KEY_HERE'

demo_colors = { 'white': '#4c4ca6', 'black':'#c77b1e', 'native':'#ff00f7', 'asian':'#c7321e', 'latino':'#3b9c3a', 'other':'#8227b0' }
vote_colors = { 'dem': 'blue', 'gop': 'red', 'other': 'purple' }

def get_population_color(df, colors):

    white = df['white']
    black = df['black']
    native = df['native']
    asian = df['asian']
    latino = df['latino']

    if white > black and white > native and white > asian and white > latino:
        return colors['white']

    if black > white and black > native and black > asian and black > latino:
      return colors['black']
    

    if native > white and native > black and native > asian and native > latino:
      return colors['native']
    
    if asian > white and asian > black and asian > native and asian > latino:
      return colors['asian']

    if latino > white and latino > black and latino > native and latino > asian:
      return colors['latino']

    return colors['other'] 

def get_vote_color(df, colors):
  
    if df['gop'] > 0.55:
        return colors['gop']

    if df['dem'] > 0.55:
        return colors['dem']

    return colors['other']


def make_feature_collection(txt):
  polygon = geojson.loads(txt)
  feature = geojson.Feature(geometry=polygon)
  return geojson.FeatureCollection([feature])

def get_district_sql(db, state, id):

  sql = f'''SELECT
state.abbreviation as abbreviation,
state.state_id as state_id,
district.district_id as district_id,
district.name as name,
district.total as population,
district.white as white,
district.latino as latino,
district.black as black,
district.asian as asian,
district.native as native,
district_voting_2020.per_gop as gop,
district_voting_2020.per_dem as dem,
district_geo.coordinates as coordinates
FROM
state
JOIN district ON state.state_id = district.state_id
JOIN district_voting_2020 ON district.district_id = district_voting_2020.district_id AND district.state_id = district_voting_2020.state_id
JOIN district_geo ON district.district_id = district_geo.district_id AND district.state_id = district_geo.state_id
WHERE
state.abbreviation = "{state}"'''
    
  if id:
    sql = sql + f'\nAND district.district_id = {id}'


  return pd.read_sql_query(sql, db)

def get_districts(db, state, id=None, demo_colors=None, vote_colors=None):

  features = []
  vcolors = []
  dcolors = []

  for index, district in get_district_sql(db, state, id).iterrows():
      if vote_colors:
        vcolor = get_vote_color(district, vote_colors)
      if demo_colors:
        dcolor = get_population_color(district, demo_colors)

      props = { 'name': district['name'], 'state': district['abbreviation'], 'population': district['population']}
      feature = geojson.Feature(properties=props, geometry=geojson.loads(district['coordinates']))
      features.append(feature)

      if vote_colors:
        vcolors.append(vcolor)
      if demo_colors:
        dcolors.append(dcolor)

  return geojson.FeatureCollection(features), vcolors, dcolors

def get_tract_sql(db, state):

  sql = f'''SELECT 
state.abbreviation as abbreviation,
state.state_id as state_id, 
county.county_id as county_id, 
county.name as county_name,
tract.tract_id  as tract_id,
tract.name as tract_name,
tract.total as population,
tract.white as white,
tract.black as black,
tract.native as native,
tract.asian as asian, 
tract.latino as latino,
tract_geo.coordinates as coordinates
FROM
state 
JOIN county ON state.state_id=county.state_id 
JOIN tract ON county.state_id=tract.state_id AND county.county_id=tract.county_id
JOIN tract_geo ON tract.state_id=tract_geo.state_id AND tract.county_id=tract_geo.county_id AND tract.tract_id=tract_geo.tract_id
WHERE 
state.abbreviation = "{state}"'''

  return pd.read_sql_query(sql, db)

def get_tracts(db, state, demo_colors=None):

  features = []
  colors = []
  
  for index, tract in get_tract_sql(db, state).iterrows():

      if demo_colors:
        color = get_population_color(tract, demo_colors)
        colors.append(color)

      props = { 'name': tract['tract_name'], 'state': tract['abbreviation'], 'population': tract['population']}
      feature = geojson.Feature(properties=props, geometry=geojson.loads(tract['coordinates']))
      features.append(feature)

  return geojson.FeatureCollection(features), colors

