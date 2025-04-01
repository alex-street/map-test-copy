import pandas as pd

mentions = pd.read_csv("../litLongData/locationmentions.csv")
documents = pd.read_csv("../litLongData/documents_genre.csv")
merged = pd.merge(mentions, documents, on='document_id', how='left')
merged = merged[merged['genre']=="crime and mystery"]
print(merged)
freq =  merged["location_id"].value_counts().to_frame(name='freq')

locations = pd.read_csv("../litLongData/locations.csv")
merged = pd.merge(merged, locations, left_on='location_id', right_on='id', how='left')


locations = pd.merge(locations, freq, left_on='id', right_on='location_id', how='right')

print(freq)

# range < 1000
# 1000 < range < 2000
# 2000 < range