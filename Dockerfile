FROM python:3.12-slim

WORKDIR /capstone-judgement-models

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .