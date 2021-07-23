FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime as nlu

ENV NLU_CACHE_DIR=/app/cache

WORKDIR /app

COPY src/libs/nlu.py .
RUN pip3 install transformers

RUN python3 nlu.py


FROM public.ecr.aws/lambda/python:3.8

ENV NLU_CACHE_DIR=/app/cache

WORKDIR /app

COPY --from=nlu /app/cache /app/cache
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src ./src/
COPY config ./config/
COPY app.py .

CMD ["/app/app.handler"]
