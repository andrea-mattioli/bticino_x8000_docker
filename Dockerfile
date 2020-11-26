ARG BASE=
FROM ${BASE} AS my_repo
FROM alpine:latest
COPY --from=my_repo /faketime.so /lib/faketime.so
ENV LD_PRELOAD=/lib/faketime.so
ENV LANG C.UTF-8
LABEL maintainer="andrea.mattiols@gmail.com"
LABEL version="2.2"
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
  && git clone -b v2 https://github.com/andrea-mattioli/bticino_X8000_rest_api.git \
  && mv bticino_X8000_rest_api/* /hassio_bticino_smarter/ \
  && rm -rf bticino_X8000_rest_api/

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY run.sh /hassio_bticino_smarter/

RUN chmod a+x /hassio_bticino_smarter/run.sh

RUN pip3 install -r requirements.txt

CMD [ "/hassio_bticino_smarter/run.sh" ]
