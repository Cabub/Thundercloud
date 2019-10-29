FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt update && apt upgrade -y && apt install -y postgresql-client
RUN pip install -r requirements.txt
COPY . /code/
CMD ./start.sh
