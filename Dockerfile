ARG ARCH=
FROM alpine
ENV TZ=Europe/Rome
ENV CLIENT_ID = recived via email
ENV CLIENT_SECRET = recived via email
ENV SUBSCRIPTION_KEY = subscription primary key
ENV DOMAIN = my home domain example.com
ENV API_USER = chose your api user
ENV API_PASS = chose your api password
ENV MQTT_BROKER = ip broker
ENV MQTT_PORT = 1883
ENV MQTT_USER = your mqtt user
ENV MQTT_PASS = your mqtt password
ENV SSL_ENABLE = 'True|False {False} for nginx proxy manager'
LABEL maintainer="andrea.mattiols@gmail.com"
LABEL version="2.1"
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
        mosquitto-clients \
    \
  && git clone https://github.com/andrea-mattioli/bticino_X8000_rest_api.git \
  && mv bticino_X8000_rest_api/* /hassio_bticino_smarter/ \
  && rm -rf bticino_X8000_rest_api/

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY run.sh /hassio_bticino_smarter/

RUN chmod a+x /hassio_bticino_smarter/run.sh

RUN pip3 install -r requirements.txt

CMD [ "/hassio_bticino_smarter/run.sh" ]
