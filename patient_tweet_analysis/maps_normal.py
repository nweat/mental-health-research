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
##http://stackoverflow.com/questions/42489881/transform-pandas-dataframe-into-frequency-matrix

lat_col = 'tweetLat'
lon_col = 'tweetLong'
weight = 'activation-pleasant'
overall_weight = 'username'
zoom_start = 5


all_normal_users = pd.read_csv('jupyter_stats/final_data/users_final_normal/labelMissingGeo_preprocessed_normalusers.csv')
all_normal_userss = all_normal_users[['tweetLat', 'tweetLong', overall_weight]]
all_normal_users_grpby_loc = all_normal_users.groupby(['tweetLat', 'tweetLong'], as_index=False)['tweetLat'].agg({overall_weight: np.size})
print all_normal_users_grpby_loc.head(10)

middle_lat_overall = all_normal_users_grpby_loc[lat_col].median()
middle_lon_overall = all_normal_users_grpby_loc[lon_col].median()


overall_spatial_dist_nrml_users = folium.Map(location=[middle_lat_overall, middle_lon_overall],
                          zoom_start=zoom_start)

#for _, row in all_bipolar_users_grpby_loc.iterrows():
	#folium.CircleMarker([row[lat_col], row[lon_col]],radius=8,popup=(str(row[lat_col])+ ' '+ str(row[lon_col])+ ' '+ str(row[overall_weight])),fill_color='#3db7e4',fill_opacity=0.9).add_to(overall_spatial_dist_bipolar_users)
# convert to (n, 2) nd-array format for heatmap
tweetLocsArr = all_normal_users_grpby_loc[[lat_col, lon_col]].as_matrix()
overall_spatial_dist_nrml_users.add_child(plugins.HeatMap(tweetLocsArr))
overall_spatial_dist_nrml_users.save('jupyter_stats/final_data/users_final_normal/spaital_dist_normal_users.html')
