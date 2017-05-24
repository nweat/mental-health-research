from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium import plugins
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import vincent

#REFERENCES
# https://alysivji.github.io/getting-started-with-folium.html
# https://github.com/python-visualization/folium/blob/master/examples/MarkerCluster.ipynb
# https://python-visualization.github.io/folium/module/element.html
# http://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/Features.ipynb
# https://blog.dominodatalab.com/creating-interactive-crime-maps-with-folium/
# create custom template: https://github.com/python-visualization/folium/issues/86

lat_col = 'tweetLat'
lon_col = 'tweetLong'
user = 'AmberNicole1205'
weight = 'activation-pleasant'
zoom_start = 5

user_details = pd.read_csv('jupyter_stats/final_data/users_final/user_list/'+user+'.csv')
#print user_details.head(10)

user_detailss = user_details[['tweetLat', 'tweetLong', weight]]
grp_by_location = user_detailss.groupby(['tweetLat', 'tweetLong'], as_index=False).agg({weight: np.mean})
grp_by_location = grp_by_location[grp_by_location[weight].notnull()]

middle_lat = grp_by_location[lat_col].median()
middle_lon = grp_by_location[lon_col].median()


clustered_points_map = folium.Map(location=[middle_lat, middle_lon],
                          zoom_start=zoom_start, 
                left='0%',
                width='50%',
                height='80%')

clustered_points = folium.features.MarkerCluster().add_to(clustered_points_map)
for _, row in grp_by_location.iterrows():
	#ranges 0 - .3, .4 - .6, .7 - 1 #"#3db7e4"
	color = ''
	if row[weight] > 0 and row[weight] <= .2: 
		color = '#FFFF00' #yellow #fee8c8
	elif row[weight] > .2 and row[weight] <= .4:
		color = '#CD8500' #orange #fdbb84
	elif row[weight] > .4 and row[weight] <= .1:
		color = '#EE4000' #red #e34a33

	folium.CircleMarker([row[lat_col], row[lon_col]],radius=8,popup=(str(row[lat_col])+ ' '+ str(row[lon_col]) + ' '+ str(row[weight]) ),fill_color=color,fill_opacity=0.9).add_to(clustered_points)
"""
folium.Marker(
    location = [row[lat_col],row[lon_col]],
    popup=(str(row[lat_col])+ ' '+ str(row[lon_col]) + ' '+ str(row[weight])),
    icon=folium.Icon(color='green', icon='ok-sign')).add_to(activation_pleasant_emotion_spatial_dist)
"""


f = folium.Figure()
#e = folium.Html("<b>tesgg</b>", width='50%', height='80%' )
f.html.add_child(folium.Element("<header style='padding: 1em;color: white;background-color: #3A5FCD;clear: left;text-align: center;font-size:14px;'>Spatio-Temporal Analysis of Bipolar Disorder - User X Dashboard of Depressive Behaviours</header>"))
f.add_child(clustered_points_map)

#f.add_child(activation_pleasant_emotion_spatial_dist)
f.save('jupyter_stats/final_data/users_final/maps/'+user+'.html')
print 'DONE'
#http://stackoverflow.com/questions/42489881/transform-pandas-dataframe-into-frequency-matrix

