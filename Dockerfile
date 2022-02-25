FROM alpine:latest
ENV LANG C.UTF-8
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
LABEL maintainer="andrea.mattiols@gmail.com"
LABEL version="2.5"
LABEL description="This is custom Docker Image for \
the Bticino X8000 Smarter API"

RUN mkdir /hassio_bticino_smarter

WORKDIR /hassio_bticino_smarter

RUN apk add --no-cache \
        bash \
        tzdata \
        python3 \
        py3-pip \
        git \
        gcc \
        mosquitto-clients \
        libressl-dev \
        musl-dev \
        libffi-dev \
        python3-dev \        
    \
  && git clone -b v2 https://github.com/andrea-mattioli/bticino_X8000_rest_api.git \
  && mv bticino_X8000_rest_api/* /hassio_bticino_smarter/ \
  && rm -rf bticino_X8000_rest_api/

COPY run.sh /hassio_bticino_smarter/

RUN chmod a+x /hassio_bticino_smarter/run.sh

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD [ "/hassio_bticino_smarter/run.sh" ]
