FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
#RUN apt update && apt upgrade -y && apt install python3-gpg
#RUN  ln -s /usr/lib/python3/dist-packages/gpg /usr/local/lib/python3.7/site-packages/gpg
RUN pip install -r requirements.txt
COPY . /code/
CMD ./start.sh
