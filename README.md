# Overpass-Turbo Backend

## Run with Docker
`docker build -t overpass_backend:latest .`

### Development
`docker run -p 8080:8080 overpass_backend:latest`

## Tests
To run the tests:

`python -m unittest tests.test_templates`
