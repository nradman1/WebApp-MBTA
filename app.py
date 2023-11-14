from flask import Flask, render_template, request
from mbta_helper import find_stop_near, weather, get_events, traintime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def search():
    #render template allows us to return the 
    if request.method == 'POST':
        place_name = request.form['place_name']
        station, accessibility = find_stop_near(place_name)
        temp = weather(place_name)
        events = get_events(place_name)
        time = traintime(place_name)
        return render_template('result.html', place_name=place_name, station=station, accessibility=accessibility, temp=temp, events=events, time = time)
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(TypeError)
def page_not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.run(debug=True)
