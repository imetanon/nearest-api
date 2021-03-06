from flask import Flask , request , Response
import json
import pandas as pd
import geopandas 
from shapely.geometry import Point
from geopy.distance import geodesic
import requests
  
app = Flask(__name__) 
  
@app.route("/") 
def home_view(): 
    return "<h1>Hello! my friends</h1>"

@app.route("/image-predict") 
def image_predict():
    p_image_url = request.args.get('p_image_url')

    params = {
        "p_image_url": p_image_url
    }
    r = requests.get('https://bit-noi-demo.herokuapp.com/predict', params=params)

    result = r.json()['result']

    contents = []
    contents.append(antenna_flex(result, p_image_url))

    payload = {
        "line_payload": [
            {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                    "type": "carousel",
                    "contents": contents
                }
            }
        ]
    }
    json_payload = json.dumps(payload)
    resp = Response(json_payload, status=200, mimetype='application/json')
    resp.headers['Response-Type'] = "object"
    
    return resp


@app.route("/nearest-check")
def nearest_check():

    latitude = request.args.get('p_latitude', 0.0)
    longtiude = request.args.get('p_longitude', 0.0)
    radius = request.args.get('radius', 15)

    location_df = pd.read_csv("./datasets/station_location.csv") 
    location_gdf = geopandas.GeoDataFrame(location_df, geometry=geopandas.points_from_xy(location_df.station_longitude, location_df.station_latitude), crs="EPSG:4326")

    user_location =[{'user':'user','latitude': latitude, 'longitude': longtiude}]
    user_df = pd.DataFrame.from_dict(user_location)
    user_gdf = geopandas.GeoDataFrame(user_df, geometry=geopandas.points_from_xy(user_df.longitude, user_df.latitude))
    user_gdf['geometry'] = user_gdf.geometry.buffer(float(radius)/100) #km
    user_gdf.set_crs(epsg=4326, inplace=True)

    intersect_station_df = geopandas.sjoin(user_gdf,location_gdf,how="left",op="contains")
    intersect_station_df['distance'] = intersect_station_df.apply(lambda x: get_distance(x.latitude, x.longitude, x.station_latitude, x.station_longitude), axis=1)

    top_five_df = intersect_station_df.sort_values('distance').head(5).reset_index()[['station_name','station_address','station_latitude','station_longitude','distance']]
    print(top_five_df)

    contents = []

    for idx in top_five_df.index: 
        contents.append(station_flex(top_five_df['station_name'][idx], top_five_df['station_address'][idx], top_five_df['distance'][idx]))
        print(top_five_df['station_name'][idx], top_five_df['station_address'][idx]) 

    payload = {
        "line_payload": [
            {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                    "type": "carousel",
                    "contents": contents
                }
            }
        ]
    }
    json_payload = json.dumps(payload)
    resp = Response(json_payload, status=200, mimetype='application/json')
    resp.headers['Response-Type'] = "object"
    
    return resp

def get_distance(src_lat, src_long, des_lat, des_long):
    coords_1 = (float(src_lat), float(src_long))
    coords_2 = (float(des_lat), float(des_long))
    return geodesic(coords_1, coords_2).km

def station_flex(name, address, distance):
    body = {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "icon",
                        "url": "https://cdn2.iconfinder.com/data/icons/communication-416/32/Communication_radio_station_signal_antena_tower-512.png",
                        "size": "xs"
                    },
                    {
                        "type": "text",
                        "text": "STATION NAME",
                        "wrap": True,
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 0,
                        "weight": "bold"
                    }
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "text",
                    "wrap": True,
                    "size": "md",
                    "text": name,
                    "weight": "bold",
                    "color": "#7F0019"
                }
                ],
                "spacing": "sm",
                "paddingBottom": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "icon",
                        "url": "https://cdn0.iconfinder.com/data/icons/map-asset-1/24/distance-512.png",
                        "size": "xs"
                    },
                    {
                        "type": "text",
                        "text": "DISTANCE",
                        "wrap": True,
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 0,
                        "weight": "bold"
                    }
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "text",
                    "wrap": True,
                    "size": "md",
                    "text": f"ระยะทาง {distance:.2f} กิโลเมตร"
                }
                ],
                "spacing": "sm",
                "paddingBottom": "md"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "icon",
                        "url": "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png",
                        "size": "xs"
                    },
                    {
                        "type": "text",
                        "text": "LOCATION",
                        "wrap": True,
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 0,
                        "weight": "bold"
                    }
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "text",
                    "text": address,
                    "wrap": True,
                    "size": "md"
                }
                ],
                "spacing": "sm",
                "paddingBottom": "md"
            }
            ],
            "paddingAll": "20px",
            "spacing": "sm",
            "action": {
            "type": "uri",
            "label": "action",
            "uri": "http://linecorp.com/"
            }
        },
        {
            "type": "separator"
        }
        ],
        "paddingAll": "0px"
    }

    footer = {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "filler"
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "filler"
                },
                {
                    "type": "text",
                    "text": "Google Maps",
                    "margin": "sm",
                    "offsetTop": "-2px",
                    "flex": 0,
                    "color": "#7F0019"
                },
                {
                    "type": "filler"
                }
                ],
                "spacing": "sm",
                "flex": 0
            },
            {
                "type": "filler"
            }
            ],
            "spacing": "sm",
            "borderWidth": "1px",
            "borderColor": "#7F0019",
            "cornerRadius": "8px",
            "height": "40px",
            "action": {
            "type": "uri",
            "label": "action",
            "uri": "http://linecorp.com/"
            }
        }
        ],
        "paddingAll": "20px",
        "spacing": "md"
    }

    bubble = {
        "type": "bubble",
        "body": body,
        "footer": footer
    }
    
    return bubble

def antenna_flex(result, image_url):

    body = {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectMode": "cover",
            "aspectRatio": "2:3",
            "gravity": "top"
        },
        {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "background": {
            "type": "linearGradient",
            "angle": "0deg",
            "startColor": "#00000099",
            "endColor": "#00000000"
            },
            "height": "60%",
            "position": "absolute",
            "width": "100%",
            "offsetEnd": "0px",
            "offsetBottom": "0px",
            "offsetStart": "0px"
        },
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "ผลการตรวจสอบ",
                    "size": "md",
                    "color": "#ffffff",
                    "weight": "bold",
                    "wrap": True,
                    "decoration": "none"
                }
                ],
                "alignItems": "center"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": f"{result.upper()}",
                    "size": "xl",
                    "color": "#ffffff",
                    "weight": "bold",
                    "wrap": True,
                    "style": "normal"
                }
                ],
                "alignItems": "center"
            }
            ],
            "position": "absolute",
            "offsetBottom": "0px",
            "offsetStart": "0px",
            "offsetEnd": "0px",
            "paddingAll": "20px",
            "paddingTop": "18px"
        }
        ],
        "paddingAll": "0px"
    }

    bubble = {
        "type": "bubble",
        "body": body
    }
    
    return bubble




