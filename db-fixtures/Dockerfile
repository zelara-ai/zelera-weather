FROM mongo

COPY fixture.json /fixture.json
CMD mongoimport --host db --db zelara_db --collection mycollection --type json --file /fixture.json --jsonArray
