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
weight = 'activation-pleasant'
overall_weight = 'username'
zoom_start = 5

user_details = pd.read_csv('jupyter_stats/final_data/users_final/user_list/50ShadesOfThisD.csv')
all_bipolar_users = pd.read_csv('jupyter_stats/final_data/users_final/labelMissingGeo_preprocessed.csv')
all_bipolar_userss = all_bipolar_users[['tweetLat', 'tweetLong', overall_weight]]
all_bipolar_users_grpby_loc = all_bipolar_userss.groupby(['tweetLat', 'tweetLong'], as_index=False)['tweetLat'].agg({overall_weight: np.size})
print all_bipolar_users_grpby_loc.head(10)

user_detailss = user_details[['tweetLat', 'tweetLong', weight]]
grp_by_location = user_detailss.groupby(['tweetLat', 'tweetLong'], as_index=False).agg({weight: np.mean})
grp_by_location = grp_by_location[grp_by_location[weight].notnull()]

middle_lat = grp_by_location[lat_col].median()
middle_lon = grp_by_location[lon_col].median()
middle_lat_overall = all_bipolar_users_grpby_loc[lat_col].median()
middle_lon_overall = all_bipolar_users_grpby_loc[lon_col].median()


clustered_points_map = folium.Map(location=[middle_lat, middle_lon],
                          zoom_start=zoom_start, position='absolute',
                left='0%',
                width='50%',
                height='50%')
"""
activation_pleasant_emotion_spatial_dist = folium.Map(location=[middle_lat, middle_lon],
                          zoom_start=zoom_start, position='absolute',
               left='50%',
               width='50%',
               height='50%')
"""

overall_spatial_dist_bipolar_users = folium.Map(location=[middle_lat_overall, middle_lon_overall],
                          zoom_start=zoom_start)

#for _, row in all_bipolar_users_grpby_loc.iterrows():
	#folium.CircleMarker([row[lat_col], row[lon_col]],radius=8,popup=(str(row[lat_col])+ ' '+ str(row[lon_col])+ ' '+ str(row[overall_weight])),fill_color='#3db7e4',fill_opacity=0.9).add_to(overall_spatial_dist_bipolar_users)
# convert to (n, 2) nd-array format for heatmap
tweetLocsArr = all_bipolar_users_grpby_loc[[lat_col, lon_col]].as_matrix()
overall_spatial_dist_bipolar_users.add_child(plugins.HeatMap(tweetLocsArr))


clustered_points = folium.features.MarkerCluster().add_to(clustered_points_map)
for _, row in grp_by_location.iterrows():
	#ranges 0 - .3, .4 - .6, .7 - 1 #"#3db7e4"
	color = ''
	if row[weight] > 0 and row[weight] <= .4: 
		color = '#FFFF00' #yellow #fee8c8
	elif row[weight] > .4 and row[weight] <= .8:
		color = '#CD8500' #orange #fdbb84
	elif row[weight] > .8 and row[weight] <= .1:
		color = '#EE4000' #red #e34a33

	folium.CircleMarker([row[lat_col], row[lon_col]],radius=8,popup=(str(row[lat_col])+ ' '+ str(row[lon_col]) + ' '+ str(row[weight]) ),fill_color=color,fill_opacity=0.9).add_to(clustered_points)
"""
folium.Marker(
    location = [row[lat_col],row[lon_col]],
    popup=(str(row[lat_col])+ ' '+ str(row[lon_col]) + ' '+ str(row[weight])),
    icon=folium.Icon(color='green', icon='ok-sign')).add_to(activation_pleasant_emotion_spatial_dist)
"""

f = folium.Figure()
f.add_child(clustered_points_map)
#f.add_child(activation_pleasant_emotion_spatial_dist)
f.save('jupyter_stats/final_data/users_final/maps/50shades.html')
overall_spatial_dist_bipolar_users.save('jupyter_stats/final_data/users_final/spaital_dist_bipolar_users.html')


#http://stackoverflow.com/questions/42489881/transform-pandas-dataframe-into-frequency-matrix