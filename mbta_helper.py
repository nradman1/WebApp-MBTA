# Your API KEYS (you need to use your own keys - very long random characters)
# from config import MAPBOX_TOKEN   #, MBTA_API_KEY
import urllib.request
import urllib.parse
import json
from geopy.distance import geodesic
from datetime import datetime, timezone

# Useful URLs (you need to add the appropriate parameters for your requests)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"
OPEN_WEATHER_BASE_URL = 'https://home.openweathermap.org/api_keys'
TICKETMASTER_BASE_URL = 'https://developer-acct.ticketmaster.com/user/44975/apps'
MAPBOX_TOKEN = 'pk.eyJ1IjoibnJhZG1hbjEiLCJhIjoiY2xvcWR3NTRvMGZrbDJsbXpiOTltbXljbCJ9.K-LMaJZ0YTq4hvWv-wklbA'
MBTA_API_KEY = '8fe44b6452254f0c8cc1ee2f001b4622'
OPEN_WEATHER_API_KEY = '51b02a09c31004514790f07183f4facd'
TICKETMASTER_API_KEY = 'c66WjahbinqiXZUj0POcpf0ibc6iP0Hw'

# A little bit of scaffolding if you want to use it
def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_long() and get_nearest_station() might need to use this function.
    """
    #1. Uses urllib.request in order to open the url, setting it equal to f
    #2. read the content and decode it as a string using UTF-8, set it equal to the response text
    #3. set the data euqal to the text converted into a dictionary of the response text
    #4. return the response data
    with urllib.request.urlopen(url) as f:
        responsetxt = f.read().decode('utf-8')
        data = json.loads(responsetxt)
        return data

def get_lat_long(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """
    #1. Replace the spaces in the place name, typical in URL coding
    #2. construct a URL to make the API request to Mapbox. Takes the URL name and the place name, and utilizes the access token for the API request in order to return the data in json format
    #3. set data euqal to the get_json function on the URL
    #4. print, within the data, get to the features line, get to the first element, go to the geometry dictionary, go to the coordinates list, select the second element, which is the latitude
    #5. same as above, except access the first element, which is the longitude at the end 
    query = place_name.replace(' ', '%20')
    url = f"{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}"
    data = get_json(url)

    latitude = str(round(float(data["features"][0]["geometry"]["coordinates"][1]),2))
    longitude = str(round(float(data["features"][0]["geometry"]["coordinates"][0]),2))

    return latitude, longitude 

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    #1. Using the MBTA base, and our inputted latitude and longitude, as well as our API key to provide authentication, use the URL
    #2. use our get_json function on our URL 
    #3, 4, 5. Set the nearest station as a empty list and smallest_distance as equal to infinity - (this ensures that we start with a value that is larger than any valid distance value that could be calculated), and the accesibility initialized as False (I added this as I had an issue as some stations did not specify their accessibility, so I needed to intialize it)
    #6. for the station within the data, in the json format of the url
        #7. the name of the station is equal to the station, attributes, and it's name
        #8. set the latitude and longitude of the station to the latitude and longitude from the function
        #9. make coordinates of the lat and long equal to the parameters of the function
        #10. make the station latitude and longitude equal to the stationlat and stationlong we got from the function
        #11. calculate the distance of the distance from the place to the station using the coordinates, I was unsure of how to get the nearest of two points using latitude and longitude, so I asked Chatgpt. It guided me to a library called geopy, which calculates the distance between two coordinates, so I used it. LINK: https://chat.openai.com/share/16815b4d-8459-4f9b-be99-11d9532fbae9
        #12.1 if the smallest distance is greater than the new distance from the station
            #12.2 set the new smallest distance to the distance
            #12.3 set the name of the nearest station to the name
            #12.4 make the acceisbility equal to 1 (True) if the wheelchair_boarding is True
    #13. return the nearest station
    radius = 0.5
    url = f"{MBTA_BASE_URL}?filter[latitude]={latitude}&filter[longitude]={longitude}&filter[radius]={radius}&api_key={MBTA_API_KEY}"
    data = get_json(url)

    nearest_station = None
    smallest_distance = float('inf')
    accessibility = False

    for station in data["data"]:
        name =  station["attributes"]["name"]

        stationlat, stationlong = get_lat_long(name)
        coord1 = float(latitude), float(longitude)
        coord2 = float(stationlat), float(stationlong)
        distance = geodesic(coord1, coord2).miles

        if smallest_distance > distance:
            smallest_distance += distance
            nearest_station = name
            accessibility = station["attributes"]["wheelchair_boarding"] == 1
            
       
        return nearest_station, accessibility


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    #1. make the longitude and latitude equal to to the long and lat from our get place name function
    #2. if the latitude and longitude is not None (I implemented this to prevent any errors)
        #3. the station and the accessibility is equal to get the nearest station of the lat and long
    #4. return the station an the accessibility
    latitude, longitude = get_lat_long(place_name)
    if latitude and longitude is not None:
        station, accessibility = get_nearest_station(latitude, longitude)
    if station == None:
        return f'There are no stations near you'
    else:
        return station, accessibility

def weather(place_name):
    """
    This function takes the name of a place and returns the weather of the place
    """
    APIKEY = OPEN_WEATHER_API_KEY
    latitude, longitude = get_lat_long(place_name)
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&APPID={APIKEY}&units=metric'
    response_data = get_json(url)
    return response_data['main']['temp']


def get_events(place_name):
    """
    This function takes the name of a place and returns events (concerts and sports games) that are going on nearby 
    """
    #1. Set the boston longitude and latitude
    #2. use the geodesic coordinates of the place name we enter, and the boston longitude and latitude
    #3.1 If the distnace to boston i sless than a 15 mile radius 
        #3.2 then change the place name to boston, do this because 10 miles from boston is relatively close, and before only Boston works as a keyword  
    #4-6. Get the API Key, State code, and country code 
    #7. Create the URL, taking into account the API Key, state code, country code, and the name of the place
    #8. One issue I noticed is that this only generated results for Boston, so using the same geopy I utilized earlier, I wanted to make everything within 15 miles (around a 30 minute drive), included in Boston
    #9-11. Open the URL text, decode it in the utf-8 format, and 
    #12.1 In the response data, get the value from the embeddedkey, and if that doesn't work then return a empty dictionary, from the embedded values, get the event key, and if that does not work return an empty list, make this equal to a list of the events
        #12.2 for the data within the list of events
        #12.3 get the name of the event, if there is no name then return nothing,
        #12.4 return the name of the event that is nearby, this will return None if there are no events neabry

    bostonlonglat = (42.3, -71.0)
    distance_to_boston = geodesic(get_lat_long(place_name), bostonlonglat).miles
    if distance_to_boston <= 15:
        place_name = "Boston"
    
    APIKEY = TICKETMASTER_API_KEY
    state_code = "MA"
    country_code = "US"
    url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={APIKEY}&stateCode={state_code}&countryCode={country_code}&keyword={place_name}'

    with urllib.request.urlopen(url) as f:
        response_text = f.read().decode('utf-8')
        response_data = json.loads(response_text)
        event_list = response_data.get('_embedded', {}).get('events', [])

        events = []
        for event_data in event_list:
            event_name = event_data.get('name', '')
            if event_name:
                events.append(event_name)
            else:
                events.append("There are no events near you")
        
        return events

def get_nearest_station_id(placename) -> str:
    """
    Given the name of the place, return the ID of the nearest MBTA station
    """
    #I made this function for the real time train function
    #1. Set the latitude and longitude to the lat and long of the place name
    #2. the nearest station is equal to the get nearest station based on the latitude and longitude, break out the _
    #3. If the nearest station is 
        #4. the radius is equal to 0.5
        #5. the url pulls the latitude and longitude and radius
        #6. the data is gotten from the url
        #7.1 for the station in the data 
            #7.2 if the station has attributes and the name equal to the nearest station we have from earlier
            #7.3 then we return the id of the station
    #8. else, return there is no id found for the station you entered 
    latitude, longitude = get_lat_long(placename)
    nearest_station, _ = get_nearest_station(latitude, longitude)

    if nearest_station:
        radius = 0.5
        url = f"{MBTA_BASE_URL}?filter[latitude]={latitude}&filter[longitude]={longitude}&filter[radius]={radius}&api_key={MBTA_API_KEY}"
        data = get_json(url)

        for station in data["data"]:
            if station["attributes"]["name"] == nearest_station:
                return station["id"]

    return "No nearest station ID found"

def traintime(placename) -> int:
    """
    Given the name of the place, get the time (in minutes) that the next train will arrive 
    """
    #by looking at the results of prediction$filter, i realized that there is no name, it it only links to the ID of the station, so I need to derive that in order to get the function to work 
    #1. set the station equal to the get nearest station id
    #2. fromt the URL, including predictions and filter, grab the information for the ID of the station
    #3. get the response data using get json
    #4. if the response data is within the data
        #5. the arrival data is euqal to the arrival time
        #6. format the arrival data to be a datetime object
        #7. get the current time using datetime now, and have it at coordinated universal time for everything as well
        #8. calculate the minutes until arrival by convering it to seconds and then into minutes, reutrn it into an integer
        #9. return the time until arrival
    #10. else, return a sorry message

    id_station = get_nearest_station_id(placename)
    url = f"https://api-v3.mbta.com/schedules?include=prediction&filter[stop]={id_station}"
    response_data = get_json(url)
    
    if response_data['data']:
        arrivaldata = response_data['data'][0]['attributes']['arrival_time']
        arrival = datetime.fromisoformat(arrivaldata)
        currentime = datetime.now(timezone.utc)
        time_until_arrival = int((arrival - currentime).total_seconds() / 60)
        return time_until_arrival
    else:
        "Sorry! There is No Prediction Available At this time"

def main():
    """
    You should test all the above functions here
    """
    place = "Wellesley"
    print(f'The latitude and longitude of {place} is {get_lat_long(place)}')
    print(f'The nearest station near the coordinates "42.248","-71.1755" is {get_nearest_station("42.248","-71.1755")}')
    result = find_stop_near(place)
    print(f'The closest stop to {place} is {result[0]} and the wheelchair accessibility is {result[1]}')
    print(f"If I live in the Metlo in Boston, the closest stop is {find_stop_near('399 Congress St, Boston, MA 02210')})")
    print(f'The weather in {place} is {weather(place)} celcius')
    print(f'The events within a 15 mile drive of {place} are {get_events(place)}')
    print(f' At {place} the next train will arrive in {traintime(place)} minutes')

if __name__ == '__main__':
    main()
