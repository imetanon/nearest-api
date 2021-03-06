from flask import Flask , request
import pandas as pd
import geopandas 
from shapely.geometry import Point
from geopy.distance import geodesic
  
app = Flask(__name__) 
  
@app.route("/") 
def home_view(): 
    return "<h1>Hello! my friends</h1>"


@app.route("/nearest-check")
def nearest_check():

    latitude = request.args.get('lat', 0.0)
    longtiude = request.args.get('long', 0.0)
    radius = request.args.get('radius', 15)

    location_df = pd.read_csv("./datasets/station_location.csv") 
    location_gdf = geopandas.GeoDataFrame(location_df, geometry=geopandas.points_from_xy(location_df.station_longitude, location_df.station_latitude), crs="EPSG:4326")

    user_location =[{'user':'user','latitude': latitude, 'longitude': longtiude}]
    user_df = pd.DataFrame.from_dict(user_location)
    user_gdf = geopandas.GeoDataFrame(user_df, geometry=geopandas.points_from_xy(user_df.longitude, user_df.latitude))
    user_gdf['geometry'] = user_gdf.geometry.buffer(float(radius)/100) #5 km
    user_gdf.set_crs(epsg=4326, inplace=True)

    intersect_station_df = geopandas.sjoin(user_gdf,location_gdf,how="left",op="contains")
    intersect_station_df['distance'] = intersect_station_df.apply(lambda x: get_distance(x.latitude, x.longitude, x.station_latitude, x.station_longitude), axis=1)

    print(intersect_station_df)

def get_distance(src_lat, src_long, des_lat, des_long):
    coords_1 = (float(src_lat), float(src_long))
    coords_2 = (float(des_lat), float(des_long))
    return geodesic(coords_1, coords_2).km



