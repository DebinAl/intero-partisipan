FROM python:3.10-bullseye
LABEL authors="Andika"

WORKDIR /app

COPY . /app

# install dependency
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload"]