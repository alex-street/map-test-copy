from flask import Flask, render_template, jsonify, send_file, request
import pandas as pd
import json
import s2cell
from os.path import relpath

app = Flask(__name__)

# DATA PREPARATION

mentions = pd.read_csv("litLongData/locationmentions.csv")
documents = pd.read_csv("litLongData/documents_genre.csv")
documents['forename'] = documents['forename'].fillna("").replace(r"^ +| +$", r"", regex=True)
documents['surname'] = documents['surname'].fillna("").replace(r"^ +| +$", r"", regex=True)
documents = documents.query("genre == ['crime and mystery','horror and ghost stories', 'thrillers and suspense']")

authors = documents[['forename', 'surname', 'gender']].drop_duplicates().sort_values(by='surname').dropna(how='any')
books = documents[['title']].drop_duplicates().sort_values(by='title').dropna(how='any')
print(authors)
sentences = pd.read_csv("litLongData/sentences.csv")
# merging mentions and documents
merged = pd.merge(mentions, documents, on='document_id', how='left').dropna(how='any')
# filtering for crime and mystery
merged = merged.query("genre == ['crime and mystery','horror and ghost stories', 'thrillers and suspense']")

locations = pd.read_csv("litLongData/locations.csv")
# merging locations with mentions and documents
merged = pd.merge(merged, locations, left_on='location_id', right_on='id', how='left')
# merging with sentences
merged = pd.merge(merged, sentences, left_on='sentence_id', right_on='id', how='left')
merged = merged[merged["text_x"]!="Edinburgh"]
merged = merged[merged["text_x"]!="Edinboro"]
print(merged.shape[0])

#print(merged)
# adding a frequency value to count how many mentions occur for each location
freq =  merged["location_id"].value_counts().to_frame(name='freq').fillna(0)
locations = pd.merge(locations, freq, left_on='id', right_on='location_id', how='right')
locations = locations[locations['freq'] > 0].drop_duplicates().sort_values(by='text')

# Function to restructure each row into the geo JSON format
def restructure(row):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row["lon"], row["lat"]]
        },
        "properties": {
            "id": row["id_x"],
            "sentence": row["text"],
            "text": row["text_x"],
            "location id": row["location_id"],
            "sentence id": row["sentence_id"],
            "title": row["title"],
            "forename": row["forename"],
            "surname": row["surname"],
            "pubyear": row["pubyear"],
            "gender": row["gender"],
            "genre": row["genre"]
        }
    }

# Convert DataFrame rows to structured JSON format
converted = merged.apply(restructure, axis=1).tolist()
geo = {
        'type': 'FeatureCollection',
        'features': converted
        }

# Route to display lat/long data
@app.route('/get_lat_long', methods=['GET'])
def get_lat_long():
    return jsonify(locations.to_dict(orient='records'))

# Route to display lat/long data
@app.route('/get_mentions', methods=['GET'])
def get_mentions():
    return json.dumps(geo, indent=4)

# Route to display lat/long data
@app.route('/get_authors', methods=['GET'])
def get_authors():
    return jsonify(authors.to_dict(orient='records'))

@app.route('/get_books', methods=['GET'])
def get_books():
    return jsonify(books.to_dict(orient='records'))

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if (request.form['fyear'] == ''):
        fyear = 0
    else:
        fyear = int(request.form['fyear'])
    if (request.form['tyear'] == ''):
        tyear = 10000
    else:
        tyear = int(request.form['fyear'])
    surname = request.form['author'].split("//")[0]
    forename = request.form['author'].split("//")[1]
    title = request.form['title']
    location = request.form['location']
    print(surname)
    print(forename)
    filtered_features = []
    #print(filtered_features)
    for feature in geo['features']:
        if ("-" in feature['properties']['pubyear'] and fyear <= int(feature['properties']['pubyear'].split("-")[0]) <= tyear) or ("/" in feature['properties']['pubyear'] and fyear <= int(feature['properties']['pubyear'].split("/")[2])):
            if (surname=="*") or (surname==feature['properties']['surname'] and forename==feature['properties']['forename']):
                if (title=="*") or (title==feature['properties']['title']):
                    if (location=="*") or (location==feature['properties']['text']):
                        filtered_features.append(feature)

    filtered_geojson = {
            "type": "FeatureCollection",
            "features": filtered_features
        }
        
    return json.dumps(filtered_geojson, indent=4)

if __name__ == '__main__':
    app.run(host='127.0.0.1',debug=True)
