import paho.mqtt.client as mqtt
import string
import yaml
import json
from bticino import send_thermostat_cmd, load_api_config_arg

qos=2
mqtt_config_file = 'config/mqtt_config.yml'
with open(mqtt_config_file, 'r') as nf:
    mqtt_cfg = yaml.safe_load(nf)
mqtt_broker=(mqtt_cfg["mqtt_config"]["mqtt_broker"])
mqtt_port=(mqtt_cfg["mqtt_config"]["mqtt_port"])
mqtt_user=(mqtt_cfg["mqtt_config"]["mqtt_user"])
mqtt_pass=(mqtt_cfg["mqtt_config"]["mqtt_pass"])
chronothermostats=load_api_config_arg("chronothermostats")
clientid = "bticino_mqtt"
topiclist=[]

for i in chronothermostats:
    mqtt_cmd_topic=(i)['chronothermostat']['mqtt_cmd_topic']
    topiclist.append(mqtt_cmd_topic)

def on_connect(client, userdata, flags, rc):  
    print("Connected with result code {0}".format(str(rc)))
    for i in topiclist:
       client.subscribe(i)  

def on_message(client, userdata, msg):
    payload_string=msg.payload.decode('utf-8')
    topic=msg.topic
    my_topic = topic.replace("cmd", "status")
    payload=send_thermostat_cmd(topic,payload_string)
    if payload != "":
       client.publish(my_topic, json.dumps(payload), qos=qos, retain=False)

client = mqtt.Client("Bticino_X8000")  
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(str(mqtt_user),str(mqtt_pass))
client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever() 
