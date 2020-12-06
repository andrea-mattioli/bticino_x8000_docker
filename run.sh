#! /bin/bash
API_PIDS=()
echo "MY VARIABLES:"
echo ""
echo ${CLIENT_ID}
echo ${CLIENT_SECRET}
echo ${SUBSCRIPTION_KEY}
echo ${DOMAIN}
echo ${HAIP}
echo ${MQTT_BROKER}
echo ${MQTT_PORT}
JSON_FILE="/config/.bticino_smarter/smarter.json"
#Check smarter file
if [ -s "$JSON_FILE" ] 
then
	echo "Smarter file already exist and contain some data."
else
	echo "Init Smarter file ..."
    mkdir -p /config/.bticino_smarter/
    mv config/smarter.json /config/.bticino_smarter/smarter.json
fi
echo "Setup config file..."
# Setup config
cat << EOF > config/config.yml
api_config:
    client_id: ${CLIENT_ID}
    client_secret: <bticino>${CLIENT_SECRET}<bticino>
    subscription_key: ${SUBSCRIPTION_KEY}
    domain: ${DOMAIN}
    haip: ${HAIP}
EOF
cat << EOF > config/mqtt_config.yml
mqtt_config:
    mqtt_broker: ${MQTT_BROKER}
    mqtt_port: ${MQTT_PORT}
    mqtt_user: ${MQTT_USER}
    mqtt_pass: ${MQTT_PASS}
EOF
# Start API
echo "Start Api"
python3 bticino.py & > /dev/null
API_PID+=($!)
# Start MQTT
sleep 3
echo "Start MQTT Client"
python3 mqtt.py & > /dev/null
API_PID+=($!)
function stop_api() {
    echo "Kill Processes..."
    kill -15 "${API_PID[@]}"
    wait "${API_PID[@]}"
    echo "Done."
}
trap "stop_api" SIGTERM SIGHUP

# Wait until all is done
wait "${API_PID[@]}"