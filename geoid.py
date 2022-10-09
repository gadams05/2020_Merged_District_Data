
geo_id = '17167001101'

state_id = int(geo_id[:2])
county_id = int(geo_id[2:5])
tract_base = int(geo_id[5:9])
tract_fraction = int(geo_id[9:])
if tract_fraction > 0:
    tract_id = tract_base + (tract_fraction/100)
else:
    tract_id = tract_base

print(f'state: {state_id} county: {county_id} tract: {tract_id}')

geo_id = '1400000US01003010704'

state_id = int(geo_id[9:11])
county_id = int(geo_id[11:14])
tract_base = int(geo_id[14:18])
tract_fraction = int(geo_id[18:])

if tract_fraction > 0:
    tract_id = tract_base + (tract_fraction/100)
else:
    tract_id = tract_base

print(f'state: {state_id} county: {county_id} tract: {tract_id}')

