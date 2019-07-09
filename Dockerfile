FROM python:3.7.3-alpine
MAINTAINER MedglobalFront

# Bu, Python'a Docker kapsayıcılarında Python çalıştırırken önerilen arabelleğe alınmamış modda çalışmasını söyler.
# Bunun nedeni Python'un çıktıları tamponlamasına izin vermemesidir.
# Sadece doğrudan onları yazdırır.
ENV PYTHONUNBUFERRED 1

# Gereksinimlerin yuklenmesi
COPY ./requirements.txt /requirements.txt

# WARNING: Ignoring APKINDEX.5a59b88b.tar.gz: No such file or directory
# WARNING: Ignoring APKINDEX.7c1f02d6.tar.gz: No such file or directory
# alttaki iki satir ustteki uyarilar icin eklendi
RUN rm -rf /var/cache/apk/* && \
    rm -rf /tmp/*
RUN apk update
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# uygulamaları çalıştıracak kullanıcıyı oluşturalım.
RUN adduser -D user
