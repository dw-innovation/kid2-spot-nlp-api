# Spot NLP API

## Run with Docker
`docker build -t kid2spotnlpapi:latest .`

## Tests
To run the tests:

`python -m unittest tests.test_templates`

## How to run
Download the models and unzip them into the model folder from the [url](https://deutschewelle-my.sharepoint.com/:f:/g/personal/ipek_baris-schlicht_dw_com/EnT844usbSZIrHM8c48IJbMB2rh4zAaDXo5dqb_EtD8xcw?e=SLumPC).
Run it as follows:
```shell
docker run -v $(pwd)/model:/app/model -p 8080:8080 --env-file .env kid2spotnlpapi:latest
```
