FROM	python:3.10-alpine
LABEL	maintainer="Derek Wan <d.wan@icloud.com>"
ENV	PYTHONUNBUFFERED	1
COPY	./requirements.txt	/requirements.txt
RUN	apk add --no-cache \
	--update \
	postgresql-client \
	jpeg-dev
RUN	apk add --no-cache \
	--update \
	--virtual \
	.tmp-apk \
	gcc \
	libc-dev \
	linux-headers \
	postgresql-dev \
	musl-dev \
	zlib \
	zlib-dev
RUN	pip install -r /requirements.txt
RUN	apk del .tmp-apk
RUN	mkdir /app
WORKDIR	/app
COPY	./app	/app
RUN	mkdir -p /vol/web/media
RUN	mkdir -p /vol/web/static
RUN	adduser -D user
RUN	chown -R user:user /vol
RUN	chmod -R 755 /vol/web
USER	user
