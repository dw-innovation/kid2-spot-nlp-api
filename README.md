# Spot NLP API
## Introduction

Spot NLP API is a service that transforms natural language queries into Intermediate Machine-Readable (IMR) format. It employs state-of-the-art transformer models along with other utilities to accomplish this task. This API also enhances its output by consulting an OSM (OpenStreetMap) tagging service. Results get stored to a MongoDB instance.

Requirements:
- Docker
- Model files
  - [T5 base model](https://huggingface.co/t5-base): files under `/model/t5-base`
  - tuned T5 model: files under `/model/t5-tuned`

## Run with Docker

Build the Docker image with:

```shell
docker build -t kid2spotnlpapi:latest .
```

Note: You might run into disk space issues after rebuilding the container a couple of times since each individual image is about 7GB in size. You can remove unused images by running `docker image prune -a` 

## How to Run
Download the models and unzip them into the model folder. Copy data/Tag_List.csv into the model folder. Run the following command:

```shell
docker run -v $(pwd)/model:/app/model -p 80:8080 --env-file .env kid2spotnlpapi:latest
```

## API Endpoints

The API currently exposes a single POST endpoint:
### `POST /transform-sentence-to-imr`
Parameters:
- `body` (JSON): A JSON object with a single key, sentence, containing the sentence to transform.

Responses
- `200 OK`: Transformation was successful. Response contains the IMR representation.
- `204 NO CONTENT`: No output was generated for the given sentence.
- `500 INTERNAL SERVER ERROR`: An internal error occurred during the transformation.

## Exception Handling

The API returns JSON formatted errors with appropriate HTTP status codes. For example, a 500 INTERNAL SERVER ERROR will be returned as:

```json
{
  "status": "error",
  "message": "<error_detail>"
}
```

## Environment Variables

The API requires the following environment variables to be set in a .env file:
- `PEFT_MODEL_ID`: Identifier for the PEFT model.
- `BASE_MODEL`: Base model for the transformer.
- `SEARCH_ENDPOINT`: The endpoint URL for OSM tag searching.
- `MONGO_URI`: MongoDB URI.
- `MONGO_DB_NAME`: MongoDB Database name.
- `MONGO_COLLECTION_NAME`: MongoDB Collection name.
- `MODEL_VERSION`: Model version in use.