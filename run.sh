#! /bin/bash
API_PIDS=()
echo "MY VARIABLES:"
echo ""
echo ${CLIENT_ID}
echo ${CLIENT_SECRET}
echo ${SUBSCRIPTION_KEY}
echo ${DOMAIN}
echo ${API_USER}
echo ${API_PASS}
echo ${MQTT_BROKER}
echo ${MQTT_PORT}
echo ${MQTT_USER}
echo ${MQTT_PASS}

my_port=$(echo ${DOMAIN} | awk -F ":" '{print $2}')
my_domain=$(echo ${DOMAIN} | awk -F ":" '{print $1}')
if [ ! -z "${my_port}" ]
  then
    REST=${DOMAIN}
    DOMAIN=$my_domain
else
    REST="${DOMAIN}:5588"
fi

mkdir ./log/

# Check Options data
if [ -z "${CLIENT_ID}" ]  || [ -z "${CLIENT_SECRET}" ] || [ -z "${SUBSCRIPTION_KEY}" ] || [ -z "${DOMAIN}" ] || [ -z "${API_USER}" ] || [ -z "${API_PASS}" ]; then
    echo "No valid options!"; exit 1
fi
if [ -z "${MQTT_BROKER}" ] || [ -z "${MQTT_PORT}" ] || [ -z "${MQTT_USER}" ] || [ -z "${MQTT_PASS}" ]; then
    echo "No valid options!"; exit 1
fi
API_PIDS=()

check_ssl () {
   CERTS=$(python3 check_cert.py ${DOMAIN})
   echo ${CERTS}
   if [ -z "${CERTS}" ]
   then
     echo "no certificate found try to generate it..."
     certbot --nginx --email admin@localhost.it --domain ${DOMAIN} -n --agree-tos --config-dir /ssl/bticino/ > /dev/null
     if [ $? != 0 ]
      then
        echo "ERROR can't validate new certificate"; exit 1
     fi
     if ! grep -q "certbot" /etc/crontabs/root
	 	ENABLE_CRON=1
      then
        echo "0 12 * * * /usr/bin/certbot renew --quiet --config-dir /ssl/bticino/ 2>&1 >> /var/log/cron" >> /etc/crontabs/root
	    ENABLE_CRON=1
     fi
   else
    echo "certificate found!"
    for i in ${CERTS}
     do
      if [[ $i == *"fullchain.pem"* ]]; then
         cert=$i
      elif [[ $i == *"privkey.pem"* ]]; then
         key=$i
      fi
    done
     sed -i -e "s~/etc/ssl/nginx/localhost.key~$key~g" /etc/nginx/nginx.conf &> /dev/null
     sed -i -e "s~/etc/ssl/nginx/localhost.crt~$cert~g" /etc/nginx/nginx.conf &> /dev/null
     kill -15 "${API_PID[@]}"
     wait "${API_PID[@]}"
     nginx & > /dev/null
	 if [ $ENABLE_CRON -eq 1 ]
	    then 
          crond & > /dev/null
     fi	 
   fi
}
if [ ${SSL_ENABLE} == true ];
then
   cp -f /etc/nginx/nginx.conf_ssl /etc/nginx/nginx.conf
   mkdir -p /etc/ssl/nginx  
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/nginx/localhost.key -out /etc/ssl/nginx/localhost.crt -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=${DOMAIN}" &> /dev/null
   sed -i -e 's/##_my_domain_##/${DOMAIN}/g' /etc/nginx/nginx.conf &> /dev/null
   nginx & > /dev/null
   API_PID+=($!)
   check_ssl
fi

echo "Setup config file..."
# Setup config
cat << EOF > config/config.yml
api_config:
    client_id: ${CLIENT_ID}
    client_secret: <bticino>${CLIENT_SECRET}<bticino>
    subscription_key: ${SUBSCRIPTION_KEY}
    domain: ${REST}
    api_user: ${API_USER}
    api_pass: ${API_PASS}
    use_ssl: ${SSL_ENABLE}
    c2c_enable: true
EOF
cat << EOF > config/mqtt_config.yml
mqtt_config:
    mqtt_broker: ${MQTT_BROKER}
    mqtt_port: ${MQTT_PORT}
    mqtt_user: ${MQTT_USER}
    mqtt_pass: ${MQTT_PASS}
EOF
# Start API
python3 bticino.py & > /dev/null
API_PID+=($!)
# Start MQTT
sleep 3
python3 mqtt.py & > /dev/null
API_PID+=($!)
if [ ${SSL_ENABLE} == true ];
 then
  echo "Api address: https://${REST}/"
 else
  echo "Api address: http://${REST}/" 
fi
function stop_api() {
    echo "Kill Processes..."
    kill -15 "${API_PID[@]}"
    wait "${API_PID[@]}"
    echo "Done."
}
trap "stop_api" SIGTERM SIGHUP

# Wait until all is done
wait "${API_PID[@]}"