# Overpass-Turbo Backend

## Run with Docker
`docker build -t overpass_backend:latest .`

### Development
`docker run -v /home/dw/Dokumente/Codes/turbopass/kid2-overpass-backend:/app -p 8080:8080 overpass_backend:latest`

## Tests
To run the tests:

`python -m unittest tests.test_templates`

Download the models and unzip until the model folder

Run it as follows:
```shell
docker run -v /home/dw/Dokumente/Codes/turbopass/kid2-overpass-backend:/app -p 8080:8080 overpass_backend:latest
```
