import glob
import io
import os
import uuid

from unidecode import unidecode

import decibel.spotifytest as sp
import decibel.framework as fw
import numpy as np
from pathlib import Path
from flask import Flask, jsonify, make_response, render_template, request, url_for, send_from_directory
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = "s3cr3t"
app.debug = False
app._static_folder = os.path.abspath("templates/static/")
app.config["CLIENT_SONGS"] = "Data/Input/Audio"
app.config["CLIENT_PREDCTIONS"] = "Data/Results/Labs/Client_Predictions/"
datalistglobal = []
actualSong = []
#Renderiza página principal
@app.route("/", methods=["GET"])
def index():
    title = "Decibel - Chord Detection"
    return render_template("layouts/index.html", title=title)

#Pega o input da pagina principal
@app.route('/', methods=['POST'])
def my_form_post():
    title = "Decibel - Chord Detection"
    text = request.form['text']
    datalistglobal.clear()
    resultado = sp.searchHtml(text)
    datalist = [resultado]
    datalistglobal.append(resultado)
    #Desenvolver a exibição de resultados de pesquisa na página results.html
    """
    for csv in glob.iglob("images/*.csv"):
        datalist.append(get_file_content(csv))
    """
    return render_template("layouts/results.html", title=title, datalist=datalist)

@app.route("/database/", methods=["GET"])
def database():
    title = "Results"
    datalist = []
    for json in glob.iglob("Data/results/Labs/Output/*.json"):
        datalist.append(json)
    return render_template("layouts/database.html", title=title, datalist=datalist)


@app.route("/results/<unique_id>", methods=["GET"])
def result_for_uuid(unique_id):
    title = "Result"
    data = get_file_content(get_file_name(unique_id))
    return render_template("layouts/result.html", title=title, data=data)


@app.route("/postmethod", methods=["POST"])
def post_javascript_data():
    jsdata = request.form["canvas_data"]
    client_prediction = json.loads(jsdata)
    print(client_prediction)
    final_prediction = []
    title = "Result"
    folder_path = Path(app.config["CLIENT_PREDCTIONS"] + actualSong[0])
    index_path = Path(app.config["CLIENT_PREDCTIONS"] + actualSong[0] + "/index.txt")
    os.makedirs(folder_path, exist_ok=True)
    folder_path.touch(exist_ok=True)
    index_path.touch(exist_ok=True)
    file = open(str(folder_path) + "/index.txt", 'r')
    index_prov = file.read()
    file.close()
    file = open(str(folder_path) + "/index.txt", 'w')
    if index_prov == '':
        file.write("1")
        index_final = '1'
    else:
        index_int = int(index_prov)
        index_int += 1
        index_final = str(index_int)
        file.write(index_final)
    file.close()


    with open(str(folder_path) + "/" + index_final + ".json", 'w') as write_file:
        for object in client_prediction:
            dictionary = {}
            dictionary['current_beat'] = object['beat']
            dictionary['current_beat_time'] = object['start']
            dictionary['estimated_chord'] = object['chord']
            final_prediction.append(dictionary)
        json.dump(final_prediction, write_file, indent=4)

    return render_template("layouts/result.html", title=title)

@app.route("/result/", methods=["GET"])
def result():
    title = "Submitted"
    return render_template("layouts/result.html", title=title)

@app.route("/results", methods=["POST"])
def contact():
        if request.form['submit_button'] == 'Select Option 1':
            song = datalistglobal[0][0][4]
            artist = datalistglobal[0][0][5]
            urltab = sp.cifra_clubify(song, artist)
            urlsong = datalistglobal[0][0][2]
            if urlsong != '' and urltab != '':
                songName = fw.predictSong(urlsong, urltab)
        elif request.form['submit_button'] == 'Select Option 2':
            song = datalistglobal[0][1][4]
            artist = datalistglobal[0][1][5]
            urltab = sp.cifra_clubify(song, artist)
            urlsong = datalistglobal[0][1][2]
            if urlsong != '' and urltab != '':
                songName = fw.predictSong(urlsong, urltab)
        elif request.form['submit_button'] == 'Select Option 3':
            song = datalistglobal[0][2][4]
            artist = datalistglobal[0][2][5]
            urltab = sp.cifra_clubify(song, artist)
            urlsong = datalistglobal[0][2][2]
            if urlsong != '' and urltab != '':
                songName = fw.predictSong(urlsong, urltab)

        actualSong.clear()
        actualSong.append(songName)
        # Returning the result to the client
        jsonPath = 'Data\Results\Labs\Output' + '/' + str(songName) + ".json"

        song = str(songName) + ".mp3"
        file = open(jsonPath, "r")
        string = file.read()
        result = json.loads(string)
        title = "Results"
        return render_template('layouts/p5page.html', title=title, result=result, songname=song)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/send_audio/<path:path>')
def send_audio(path):
    try:
        return send_from_directory(app.config["CLIENT_SONGS"], path, as_attachment=True)
    except FileNotFoundError:
        print('Error 404')

def create_csv(text):
    unique_id = str(uuid.uuid4())
    with open(get_file_name(unique_id), "a") as file:
        file.write(text[1:-1] + "\n")
    return unique_id


def get_file_name(unique_id):
    return f"Data/results/Labs/Output/{unique_id}"


def get_file_content(filename):
    with open(filename, "r") as file:
        return file.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
