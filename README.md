# GeoDemo

This project is a massive dataset that combines Census Tracts, population data, and demographic data from the 2020 Census with the congressional districts used in the 116th congress. Combined, these pieces of data can be used for a range of research projects in the field of election analysis. I used this dataset in my own research uses regarding gerrymandering in congressional districts and looking more objective district lines and the changes in both the demographic makeup in those potential districts and the election results that might result from them. 

## Some examples below:

### Loading districts for a state, then highlighting a single district

```python
figure_layout = {
    'width': '2000px',
    'height': '2000px',
    'border': '1px solid black',
    'padding': '1px'
}
fig = gmaps.figure(layout=figure_layout)

feature_coll,v,d = gd.get_districts(db, 'NY')
hilight_coll,v,d = gd.get_districts(db, 'NY', 17)

gini_layer = gmaps.geojson_layer(feature_coll, fill_opacity=0.0, stroke_weight=2)
fig.add_layer(gini_layer)

hilight_layer = gmaps.geojson_layer(hilight_coll, fill_opacity=0.75, fill_color=['gray'], stroke_weight=2)
fig.add_layer(hilight_layer)

fig
```

![district example](/demo/district.jpg)

### Loading census tracts and coloring for the largest demographic 

```python
fig = gmaps.figure(layout=figure_layout)
feature_coll, demo_colors = gd.get_tracts(db, 'IL', demo_colors=gd.demo_colors)
gini_layer = gmaps.geojson_layer(feature_coll, fill_color=demo_colors, fill_opacity=0.5, stroke_weight=2)
fig.add_layer(gini_layer)

fig
```

![tract example](/demo/tract.jpg)

### Loading census tracts and coloring for the largest demographic, then layering districts on top, colored by outcome of 2020 presidential election.

```python
fig = gmaps.figure(layout=figure_layout)
state =   'TX'
feature_coll, demo_colors = gd.get_tracts(db, state, demo_colors=gd.demo_colors)
gini_layer = gmaps.geojson_layer(feature_coll, fill_color=demo_colors, fill_opacity=0.5, stroke_weight=2)
fig.add_layer(gini_layer)

feature_coll, vote_colors, demo_colors = gd.get_districts(db, state, demo_colors=gd.demo_colors, vote_colors=gd.vote_colors)
gini_layer = gmaps.geojson_layer(feature_coll, fill_color=demo_colors, stroke_color=vote_colors, fill_opacity=0.0, stroke_opacity=1.0, stroke_weight=5)
fig.add_layer(gini_layer)

fig
```

![tract example](/demo/district-tract.jpg)

## Requirements

main.py builds a sqlite3 database file. Also, a prebuilt database file is available [here](https://drive.google.com/file/d/13Lff2690yTfAK6spUXJSNx1Ad4dKvb92/view).

To use in a jupyter notebook, first install the excellent [jupyter-gmaps](https://jupyter-gmaps.readthedocs.io/en/latest/) plugin and get an API key for Google Maps [here](https://developers.google.com/maps/documentation/javascript/get-api-key). Then use the helper functions in geodemo.py to generate the GeoJSON layers. See example [here](/geodemo.ipynb).

Please report issues to the [issues tracker](https://github.com/gadams05/GeoDemo/issues). Thanks for using geodemo I hope you find it useful.

--Graham



