from flask import Flask,redirect, url_for,request,render_template,make_response,session,jsonify
from flask_restful import Api, Resource, reqparse
import googlemaps
from datetime import datetime
from datetime import timedelta
import time
import responses
import requests
import json
import sys
import time
from datetime import datetime

app = Flask(__name__)
api = Api(app)
# defining parser
app.secret_key='Axcv'
parser = reqparse.RequestParser()
parser.add_argument('params', type=list)
gmaps = googlemaps.Client(key='AIzaSyAs2R7yNwrbyJlaGpWaUycJDGgE2lR0pcM')

@app.route('/')
def index_page():
   return render_template('projectindex.html')

@responses.activate
@app.route('/routes')
def getRoute():
    responses.add(responses.GET,
            'https://maps.googleapis.com/maps/api/directions/json',
             body='{"status":"OK"}',
             status=200,
             content_type='application/json'
             )
    origin = str(request.args.get('origin'))
    destination = str(request.args.get('destination'))
    mode = str(request.args.get('mode'))
    mode = mode.lower()
    start = time.time()
    print("Start - "+str(start),file=sys.stderr)
    # calling google map API for getting direcction
    routes = gmaps.directions(origin,destination,mode=mode)
    #print(type(routes),file =sys.stderr)
    route_list = routes[0]
    leg_list= route_list['legs']
    leg_1 = leg_list[0]
    steps = leg_1['steps']
    url = 'https://api.openweathermap.org/data/2.5/weather?appid=bc313bb2bae300dbf7a8449101874ac0'
    weather_data = []
    for i in range(len(steps)):
                     step = steps[i]
                     location = step['start_location']
                     lat = location['lat']
                     lng = location['lng']
                     req_url = url+'&lat='+str(lat)+'&lon='+str(lng)
                     reverse_geocode = gmaps.reverse_geocode((lat, lng))
                     address = reverse_geocode[2]
                     #print("formatted addr")
                     formatted_address = address['formatted_address']
                     #print(formatted_address,file=sys.stderr)
                     split_address = formatted_address.split(",")
                     city = split_address[1]
                     #print(city,file=sys.stderr)
                     weather_response = requests.get(req_url)
                     weather= json.loads(weather_response.text)
                     weather_obj = weather['weather']
                     weather_main = weather['main']
                     temp = weather_main['temp']
                     temp = temp - 273.15
                     weather_object = weather_obj[0]
                     weather_object['temperature'] = temp
                     step['weather_info'] = weather_object
                     step['city'] = city
             
    end = time.time()
    print("End - "+str(end),file=sys.stderr)
    print('API Query Cost - '+str(end-start))
    return jsonify({"routes":routes})

if __name__ == '__main__':
   app.run(debug = True)

