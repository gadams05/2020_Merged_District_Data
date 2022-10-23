# GeoDemo

This project is a massive dataset that combines Census Tracts, population data, and demographic data from the 2020 Census with the congressional districts used in the 116th congress. Combined, these pieces of data can be used for a range of research projects in the field of election analysis. I used this dataset in my own research uses regarding gerrymandering in congressional districts and looking more objective district lines and the changes in both the demographic makeup in those potential districts and the election results that might result from them. 

Some examples below:

## Loading districts for a state, then highlighting a single district

```
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

