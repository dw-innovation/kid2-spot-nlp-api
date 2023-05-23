# Overpass-Turbo Backend

## Run with Docker
`docker build -t overpass_backend:latest .`

### Development
`docker run -v /home/dw/Dokumente/Codes/turbopass/kid2-overpass-backend:/app -p 8080:8080 overpass_backend:latest`

## Tests
To run the tests:

`python -m unittest tests.test_templates`

Download the models and unzip them into the model folder from the [url](https://deutschewelle-my.sharepoint.com/:f:/g/personal/ipek_baris-schlicht_dw_com/EnT844usbSZIrHM8c48IJbMB2rh4zAaDXo5dqb_EtD8xcw?e=SLumPC).

Run it as follows:
```shell
docker run -v /home/dw/Dokumente/Codes/turbopass/kid2-overpass-backend:/app -p 8080:8080 overpass_backend:latest
```
