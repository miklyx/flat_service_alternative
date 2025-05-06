# Flat Service FastAPI

A FastAPI-based service for collecting Berlin flats information.

## Features

- Runs own telegram client to read data from channels
- Database integration with redis and postgres
- Periodicaly asks for new data in sources
- Put "hot" data to redis, all data to Postgres
- Had endpoints to see statistics

## Installation

Create virtual environment, then:

```bash
pip install -r requirements.txt
```

## Usage

```bash
uvicorn main:app --reload
```

## API Documentation

Access the API documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## License

MIT