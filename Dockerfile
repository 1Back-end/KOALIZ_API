FROM python:3.12.3

#Todo change timezone base on projet 
# ENV TZ=Europe/Berlin 
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get install -y \
    curl \
    gcc \
    git \
    vim \
    libxrender1 \
    libfontconfig \
    libxtst6 \
    xz-utils

RUN apt-get install -y libxslt-dev libxml2-dev libpam-dev libedit-dev python-dev-is-python3 locales

RUN sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

RUN mkdir /webapp
RUN mkdir -p /webapp/alembic/versions


COPY ./requirements.txt /webapp/
WORKDIR /webapp

RUN python3 -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /webapp

RUN mkdir /webapp/uploads

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--port=80", "--host=0.0.0.0"]
