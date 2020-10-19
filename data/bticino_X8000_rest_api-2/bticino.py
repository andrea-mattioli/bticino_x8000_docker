from flask import  Flask,jsonify,request,session,redirect,render_template,url_for,send_from_directory,Response
import flask
import random
import string
import json
import requests
import yaml
import time
import datetime
import threading
import os
import re
import sys
import shutil
import jinja2
from jinja2 import Template
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
from pathlib import Path
def randomStringDigits(stringLength=32):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
oauth2_url="https://partners-login.eliotbylegrand.com/authorize"
token_url="https://partners-login.eliotbylegrand.com/token"
devapi_url="https://api.developer.legrand.com/smarther/v2.0"
thermo_url=devapi_url+"/chronothermostat/thermoregulation/addressLocation"
state=randomStringDigits()
config_file = 'config/config.yml'
mqtt_config_file = 'config/mqtt_config.yml'
api_config_file = ''
tmp_api_config_file = 'config/smarter.json'
static_api_config_file = '/config/.bticino_smarter/smarter.json'
package_template = 'templates/package.yml.jinja2'
package_config_file = '/config/packages/bticino_x8000.yaml'
flag_connected = 0
open_list = ["[","{","("] 
close_list = ["]","}",")"]

def check_config_file():
    global api_config_file
    Path("/config/.bticino_smarter/").mkdir(parents=True, exist_ok=True)
    if not os.path.exists(static_api_config_file) or os.path.getsize(static_api_config_file) == 0:
       api_config_file = 'config/smarter.json'
       return True
    else:
       api_config_file = '/config/.bticino_smarter/smarter.json'
       return False

check_config_file()
    
with open(config_file, 'r') as f:
    cfg = yaml.safe_load(f)
client_id=(cfg["api_config"]["client_id"])
client_secret_file=str((cfg["api_config"]["client_secret"]))
client_secret=re.search('<bticino>(.*?)<bticino>', client_secret_file).group(1)
subscription_key=(cfg["api_config"]["subscription_key"])
domain=(cfg["api_config"]["domain"])
haip=(cfg["api_config"]["haip"])
redirect_url="https://"+domain+"/api/webhook/mattiols_x_8000"
redirect_code_url="http://"+haip+":5588"+"/callback"

with open(mqtt_config_file, 'r') as nf:
    mqtt_cfg = yaml.safe_load(nf)
mqtt_broker=(mqtt_cfg["mqtt_config"]["mqtt_broker"])
mqtt_port=(mqtt_cfg["mqtt_config"]["mqtt_port"])
mqtt_user=(mqtt_cfg["mqtt_config"]["mqtt_user"])
mqtt_pass=(mqtt_cfg["mqtt_config"]["mqtt_pass"])

app = Flask(__name__)
def check_empty_item(item):
    json_object=get_json()
    if len(json_object['api_requirements'][item]) < 1:
       return True
    else:
       return False
 
def check(myStr): 
    stack = [] 
    for i in myStr: 
        if i in open_list: 
            stack.append(i) 
        elif i in close_list: 
            pos = close_list.index(i) 
            if ((len(stack) > 0) and
                (open_list[pos] == stack[len(stack)-1])): 
                stack.pop() 
            else:
                return False
    if len(stack) == 0:
        return True
    else:
        return False

def repair_json():
    a_file = open(api_config_file, "r")
    f=a_file.read()
    while not check(f):
       f = f[:-1]
    a_file.close()
    a_file = open(api_config_file, "w")
    a_file.write(f)
    a_file.close()
    a_file = open(api_config_file, "r")
    try:
      json_object = json.load(a_file)
      a_file.close()
      return json_object
    except:
      pass

def get_json():
    a_file = open(api_config_file, "r")
    try:
      json_object = json.load(a_file)
      a_file.close()
      return json_object
    except:
      json_object=repair_json()
      return json_object

def write_json(json_object):
    a_file = open(api_config_file, "w")
    json.dump(json_object, a_file)
    a_file.close()
def update_api_config_file_code(code):
    json_object=get_json()
    json_object['api_requirements']['code'] = code
    write_json(json_object)
def update_api_config_file_access_token(access_token):
    json_object=get_json()
    json_object['api_requirements']['access_token'] = access_token
    write_json(json_object)
def update_api_config_file_refresh_token(refresh_token):
    json_object=get_json()
    json_object['api_requirements']['refresh_token'] = refresh_token
    write_json(json_object)
def update_api_config_file_my_plants(my_plants):
    json_object=get_json()
    json_object['api_requirements']['my_plants'] = my_plants
    write_json(json_object)
def update_api_config_file_chronothermostats(chronothermostats):
    json_object=get_json()
    json_object['api_requirements']['chronothermostats'] = chronothermostats
    write_json(json_object)
def update_api_config_file_my_programs(my_programs_array):
    json_object=get_json()
    json_object['api_requirements']['chronothermostats']['programs'] = my_programs_array
    write_json(json_object)

def load_api_config():
    json_object=get_json()
    code = json_object['api_requirements']['code']
    access_token = json_object['api_requirements']['access_token']
    refresh_token = json_object['api_requirements']['refresh_token']
    my_plants = json_object['api_requirements']['my_plants']
    chronothermostats = json_object['api_requirements']['chronothermostats']
    return code, access_token, my_plants, chronothermostats, refresh_token
def load_api_config_arg(arg):
    json_object=get_json()
    if arg == "code":
       arg = json_object['api_requirements']['code']
    if arg == "access_token":
       arg = json_object['api_requirements']['access_token']
    if arg == "refresh_token":
       arg = json_object['api_requirements']['refresh_token']
    if arg == "my_plants":
       arg = json_object['api_requirements']['my_plants']
    if arg == "chronothermostats":
       arg = json_object['api_requirements']['chronothermostats']
    return arg 
@app.route('/rest')
def rest_api():
    response=rest()
    parse_response(json.dumps(response))   
    return Response(json.dumps(response),  mimetype='application/json')
@app.route('/info')
def info():
    my_value_tamplate=rest()
    parse_response(json.dumps(my_value_tamplate))
    return render_template('info.html', j_response=my_value_tamplate)

@app.route('/create_entities')
def create_entities():
    Path("/config/packages").mkdir(parents=True, exist_ok=True)
    with open(package_template) as file_:
        template = Template(file_.read())
    chronothermostats=load_api_config_arg("chronothermostats")
    my_programs_array=[]
    my_chronothermostat_array=[]
    for i in chronothermostats:                                                                                  
        name=(i)['chronothermostat']['name']                                                                                      
        mqtt_status_topic=(i)['chronothermostat']['mqtt_status_topic']                  
        mqtt_cmd_topic=(i)['chronothermostat']['mqtt_cmd_topic']
        programs=(i)['chronothermostat']['programs']
        for program in programs:
            my_program_name=program['program_name']
            if my_program_name != "0":
               my_programs_array.append(my_program_name)
        if not my_programs_array:
            my_programs_array.append('No Program')
        my_chronothermostat_array.append({"name":name.lower(), "mqtt_status_topic":mqtt_status_topic, "mqtt_cmd_topic":mqtt_cmd_topic, "programs":my_programs_array})
        my_programs_array=[]
    json_object=json.dumps(my_chronothermostat_array)
    my_value_template = json.loads(json_object)
    f = open(package_config_file, "w+")
    f.write(template.render(j_response=my_value_template, haip=redirect_code_url))
    f.close()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/c2c_subscription')
def get_c2c_subscription():
    access_token=load_api_config_arg("access_token")
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json',
    }
    payload = ''
    c2c=[]
    try:
        response = requests.request("GET", devapi_url+"/subscription", data = payload, headers = headers)
        for j in json.loads(response.text):
           plantId=(j['plantId'])
           EndPointUrl=(j['EndPointUrl'])
           subscriptionId=(j['subscriptionId'])
           c2c.append({ 'plantId':plantId, 'subscriptionId':subscriptionId, 'EndPointUrl':EndPointUrl })
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return False
    return render_template('c2c_subscription.html', c2c_conf=c2c)

@app.route('/c2c_remove')
def remove_c2c_subscription():
    plantId = request.args.get('plantId')
    subscriptionId = request.args.get('subscriptionId')
    access_token=load_api_config_arg("access_token")
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json',
    }
    payload = ''
    try:        
        response = requests.request("DELETE", devapi_url+"/plants/"+plantId+"/subscription/"+subscriptionId, data = payload, headers = headers)
        if response.status_code == 200:
           return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        else:
           return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'} 

def rest():
    access_token=load_api_config_arg("access_token")
    chronothermostats=load_api_config_arg("chronothermostats")
    chronothermostats_status=[]
    for i in chronothermostats:                                                         
        plantid=(i)['chronothermostat']['plant']                                        
        topologyid=(i)['chronothermostat']['topology']                                  
        name=(i)['chronothermostat']['name']                                            
        c2c=(i)['chronothermostat']['c2c']                                              
        mqtt_status_topic=(i)['chronothermostat']['mqtt_status_topic']                  
        mqtt_cmd_topic=(i)['chronothermostat']['mqtt_cmd_topic']                        
        mode,function,state,setpoint,temperature,temp_unit,humidity,my_program_name,remaining_time,remaining_time_minutes = get_status(access_token,plantid,topologyid)
        chronothermostats_status.append({ "name": name, "mode" : mode, "function" : function ,  "state" : state, "setpoint" : setpoint, "temperature" : temperature, "temp_unit" : temp_unit, "humidity" : humidity, "program" : my_program_name, "c2c-subscription": c2c, "mqtt_status_topic":mqtt_status_topic, "mqtt_cmd_topic":mqtt_cmd_topic, "remaining_time":remaining_time, "remaining_time_minutes":remaining_time_minutes})
    return chronothermostats_status

@app.route('/')
def get_token(my_url=None):
    my_url = oauth2_url+"?client_id="+client_id+"&response_type=code"+"&state="+state+"&redirect_uri="+redirect_code_url
    #my_url = oauth2_url+"?client_id="+client_id+"&response_type=code"+"&state="+state+"&redirect_uri="+"http://192.168.1.178:5588/callback"
    return render_template('index.html', code_url=my_url)

def get_access_token(code):
    body = {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "client_secret": client_secret,
        }
    response = requests.request("POST", token_url, data = body)
    access_token = json.loads(response.text)['access_token']
    refresh_token = json.loads(response.text)['refresh_token']
    return access_token, refresh_token

def f_refresh_token():
       if not check_empty_item("refresh_token"):
          refresh_token=load_api_config_arg("refresh_token")
          body = {
                  "client_id": client_id,
                  "grant_type": "refresh_token",
                  "refresh_token": refresh_token,
                  "client_secret": client_secret,
              }
          try:
            response = requests.request("POST", token_url, data = body)
            access_token = json.loads(response.text)['access_token']
            update_api_config_file_access_token(access_token)
            refresh_token = json.loads(response.text)['refresh_token']
            update_api_config_file_refresh_token(refresh_token)
          except:
              pass

def get_plants(access_token):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
    }
    payload = ''
    try:
        response = requests.request("GET", devapi_url+"/plants", data = payload, headers = headers)
        plants = json.loads(response.text)['plants']
        my_plants=[]
        for plan in plants:
            my_plant_id=(plan['id'])
            my_plant_name=(plan['name'])
            my_plants.append({"plant":{"id":my_plant_id, "name":my_plant_name}})
        return my_plants
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_topology(access_token,my_plants):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
    }
    payload = ''
    try:
        chronothermostats=[]
        for plant_id in my_plants:
            plant=(plant_id)['plant']['id']
            response = requests.request("GET", devapi_url+"/plants/"+plant+"/topology", data = payload, headers = headers)
            topologys = json.loads(response.text)['plant']['modules']
            plant_r = json.loads(response.text)['plant']['id']
            if f_c2c_subscribe(access_token,plant):
               c2c = "Enable"
            else:
               c2c = "Disable"
            if plant == plant_r:
               for topology in topologys:
                   topologyid=(topology['id'])
                   topologyname=(topology['name'])
                   mqtt_status_topic="/bticino/"+topologyid+"/status"
                   mqtt_cmd_topic="/bticino/"+topologyid+"/cmd"
                   Null,programs=get_programs_name(access_token, plant, topologyid)
                   chronothermostats.append({"chronothermostat":{"plant":plant, "topology":topologyid, "name":topologyname, "c2c":c2c, "mqtt_status_topic":mqtt_status_topic, "mqtt_cmd_topic":mqtt_cmd_topic, "programs":programs}})
        return chronothermostats
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_programs_name(access_token,plantid,topologyid):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
    }
    payload = ''
    try:
        my_programs_array=[]
        response = requests.request("GET", thermo_url+"/plants/"+plantid+"/modules/parameter/id/value/"+topologyid+"/programlist", data = payload, headers = headers)
        chronothermostats = json.loads(response.text)['chronothermostats']
        for chronothermostat in chronothermostats:
            programs=(chronothermostat['programs'])
            for program in programs:
                my_program_number=program['number']
                my_program_name=program['name']
                my_programs_array.append({"program_number":my_program_number, "program_name":my_program_name}) 
        return my_program_name,my_programs_array
    except:
        pass
def get_programs_name_from_local(topologyid,program_number):
    chronothermostats_stored=load_api_config_arg("chronothermostats")
    for c in chronothermostats_stored:
        topology = c['chronothermostat']['topology']
        my_programs = c['chronothermostat']['programs']
        if topology == topologyid:
           for prg in my_programs:
               my_program_number=prg['program_number']
               if int(my_program_number) == int(program_number):
                   my_program_name=prg['program_name']
                   return my_program_name   

def get_programs_number_from_local(topologyid,program_name):
    chronothermostats_stored=load_api_config_arg("chronothermostats")
    for c in chronothermostats_stored:
        topology = c['chronothermostat']['topology']
        my_programs = c['chronothermostat']['programs']
        if topology == topologyid:
           for prg in my_programs:
               my_program_name=prg['program_name']
               if my_program_name == program_name:
                   my_program_number=prg['program_number']
                   return my_program_number

def get_status(access_token,plantid,topologyid):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
    }
    payload = ''
    try:
        response = requests.request("GET", thermo_url+"/plants/"+plantid+"/modules/parameter/id/value/"+topologyid, data = payload, headers = headers)
        chronothermostats = json.loads(response.text)['chronothermostats']
        for chronothermostat in chronothermostats:
            function=(chronothermostat['function'])
            mode=(chronothermostat['mode'])
            state=(chronothermostat['loadState'])
            setpoint=(chronothermostat['setPoint']['value'])
            temp_unit=(chronothermostat['temperatureFormat'])
            thermometers=(chronothermostat['thermometer']['measures'])
            remaining_time=None
            remaining_time_minutes=None
            try:
                activationTime=(chronothermostat['activationTime'])
                date2=(datetime.datetime.strptime(activationTime, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now())
                remaining_time_minutes = str(date2.total_seconds() / 60).split(".")[0]
                remaining_time="h e ".join(str(datetime.datetime.strptime(activationTime, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now()).split(".")[0].split(":", 2)[:2])+"m"
                if "0h e" in remaining_time:
                   remaining_time=remaining_time.split("0h e ")[1]
            except:
                pass
            programs=(chronothermostat['programs'])
            for prog in programs:
                program_number = prog['number']
                program_name = get_programs_name_from_local(topologyid, program_number)
            for thermometer in thermometers:
                temperature=thermometer['value']
            hygrometers=(chronothermostat['hygrometer']['measures'])
            for hygrometer in hygrometers:
                humidity=hygrometer['value']
        return mode,function,state,setpoint,temperature,temp_unit,humidity,program_name,remaining_time,remaining_time_minutes
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def f_c2c_subscribe(access_token,plantid):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json',
    }   
    payload = {
               "EndPointUrl": redirect_url,
               "description": "Rest Api",
              }
    try:
       response = requests.request("POST", devapi_url+"/plants/"+plantid+"/subscription", data = json.dumps(payload), headers = headers)
       if response.status_code == 201:
          return True
       if response.status_code == 409:
          return True
       else:
          return False
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return False

def set_payload(arg,function,mode,setPoint,temp_unit,program):
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    boost_30=(datetime.datetime.now() + datetime.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    boost_60=(datetime.datetime.now() + datetime.timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
    boost_90=(datetime.datetime.now() + datetime.timedelta(minutes=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if arg == "AUTOMATIC":
       payload = {
        "function": function,
        "mode": "automatic",
        "setPoint": {
          "value": setPoint,
          "unit": temp_unit
        },
        "programs": [
          {
            "number": program
          }
        ]
       }
    elif arg == "MANUAL":
       payload = {
        "function": function,
        "mode": "manual",
        "setPoint": {
          "value": setPoint,
          "unit": temp_unit
        }
       }
    elif arg == "BOOST-30":
       payload = {
        "function": function,
        "mode": "boost",
        "activationTime":date+"/"+boost_30,
        "setPoint": {
          "value": setPoint,
          "unit": temp_unit
        }
       }
    elif arg == "BOOST-60":
       payload = {
        "function": function,
        "mode": "boost",
        "activationTime":date+"/"+boost_60,
        "setPoint": {
          "value": setPoint,
          "unit": temp_unit
        }
       }
    elif arg == "BOOST-90":
       payload = {
        "function": function,
        "mode": "boost",
        "activationTime":date+"/"+boost_90,
        "setPoint": {
          "value": setPoint,
          "unit": temp_unit
        }
       }
    elif arg == "OFF":
       payload = {
        "function": function,
        "mode": "off",
       }
    elif arg == "PROTECTION" or arg == "off":
       payload = {
        "function": function,
        "mode": "protection",
       }
    elif arg == "HEATING" or arg == "heat":
       if mode == "PROTECTION" or mode == "OFF":
          payload = {
           "function": "heating",
           "mode": "automatic",
           "setPoint": {
             "value": setPoint,
             "unit": temp_unit
           },
           "programs": [
             {
               "number": program
             }
           ]
          }
       else:
          payload = {
           "function": "heating",
           "mode": mode,
           "setPoint": {
             "value": setPoint,
             "unit": temp_unit
           },
           "programs": [
             {
               "number": program
             }
           ]
          }          
    elif arg == "COOLING" or arg == "cool":
       if mode == "PROTECTION" or mode == "OFF":
          payload = {
           "function": "cooling",
           "mode": "automatic",
           "setPoint": {
             "value": setPoint,
             "unit": temp_unit
           },
           "programs": [
             {
               "number": program
             }
           ]
          }
       else:
          payload = {
           "function": "cooling",
           "mode": mode,
           "setPoint": {
             "value": setPoint,
             "unit": temp_unit
           },
           "programs": [
             {
               "number": program
             }
           ]
          }
    elif arg.replace('.', '', 1).isdigit():
       payload = {
        "function": function,
        "mode": "manual",
        "setPoint": {
          "value": arg,
          "unit": temp_unit
        }
       }
    elif "m" or "h" or "d" in arg:
       if "m" in arg:
         number=(arg.split(" ",1)[1].split("m",1)[0])
         value=(arg.split(" ",1)[0])
         to_date=(datetime.datetime.now() + datetime.timedelta(minutes=int(number))).strftime("%Y-%m-%dT%H:%M:%SZ")
       elif "h" in arg:
         number=(arg.split(" ",1)[1].split("h",1)[0])
         value=(arg.split(" ",1)[0])
         to_date=(datetime.datetime.now() + datetime.timedelta(hours=int(number))).strftime("%Y-%m-%dT%H:%M:%SZ")
       elif "d" in arg:
         number=(arg.split(" ",1)[1].split("d",1)[0])
         value=(arg.split(" ",1)[0])
         to_date=(datetime.datetime.now() + datetime.timedelta(days=int(number))).strftime("%Y-%m-%dT%H:%M:%SZ")
       if value == "OFF":
          payload = {
           "function": function,
           "mode": "off",
           "activationTime":date+"/"+to_date,
          }
       else:
           payload = {
            "function": function,
            "mode": "manual",
            "activationTime":date+"/"+to_date,
            "setPoint": {
              "value": value,
              "unit": temp_unit
            }
           }
    return payload

def send_thermostat_cmd(mqtt_cmd_topic, arg):
    access_token=load_api_config_arg("access_token")
    chronothermostats=load_api_config_arg("chronothermostats")
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key ,
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json',
    }
    try:
       get_actual_state=rest()
       for i in get_actual_state:
           my_mqtt_cmd_topic=(i)['mqtt_cmd_topic']
           for j in chronothermostats:
               my_stored_mqtt_cmd_topic=(j)['chronothermostat']['mqtt_cmd_topic']
               if mqtt_cmd_topic == my_mqtt_cmd_topic == my_stored_mqtt_cmd_topic:
                  programs_avail=(j)['chronothermostat']['programs']
                  plantid=(j)['chronothermostat']['plant']
                  topologyid=(j)['chronothermostat']['topology']
                  name=(j)['chronothermostat']['name']
                  mode=(i)['mode']
                  function=(i)['function']
                  setPoint=(i)['setpoint']
                  temp_unit=(i)['temp_unit']
                  program_name=(i)['program']                   
                  program=(get_programs_number_from_local(topologyid, program_name))
                  for prg in programs_avail:
                      if arg == (prg)['program_name']:
                         program = (prg)['program_number']
                         arg="AUTOMATIC"
       payload = set_payload(arg,function,mode,setPoint,temp_unit,program)
       response = requests.request("POST", devapi_url+"/chronothermostat/thermoregulation/addressLocation/plants/"+plantid+"/modules/parameter/id/value/"+topologyid, data = json.dumps(payload), headers = headers)
       if response.status_code == 200:
          get_actual_state=rest()
          for i in get_actual_state:
              my_mqtt_cmd_topic=(i)['mqtt_cmd_topic']
              for j in chronothermostats:
                  my_stored_mqtt_cmd_topic=(j)['chronothermostat']['mqtt_cmd_topic']
                  if mqtt_cmd_topic == my_mqtt_cmd_topic == my_stored_mqtt_cmd_topic:
                     plantid=(j)['chronothermostat']['plant']
                     programs_avail=(j)['chronothermostat']['programs']
                     topologyid=(j)['chronothermostat']['topology']
                     name=(j)['chronothermostat']['name']
                     mode=(i)['mode']
                     state=(i)['state']
                     temperature=(i)['temperature'] 
                     humidity=(i)['humidity'] 
                     function=(i)['function']
                     setPoint=(i)['setpoint']
                     temp_unit=(i)['temp_unit']
                     program=(i)['program']
                     remaining_time=(i)['remaining_time']
                     remaining_time_minutes=(i)['remaining_time_minutes']
          response_payload= { "name": name, "mode" : mode, "function" : function ,  "state" : state, "setpoint" : setPoint, "temperature" : temperature, "temp_unit" : temp_unit, "humidity" : humidity, "program" : program, "remaining_time":remaining_time, "remaining_time_minutes":remaining_time_minutes }
          return response_payload 
       else:
          return False
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return False
    
def schedule_update_token():
    f_refresh_token()
    scheduler = BackgroundScheduler()
    scheduler.add_job(f_refresh_token, 'interval', minutes=50)
    scheduler.start()
schedule_update_token()

def b_mqtt(mqtt_status_topic, data):
    subprocess.call(["mosquitto_pub", "-h", str(mqtt_broker), "-p", str(mqtt_port), "-u", str(mqtt_user), "-P", str(mqtt_pass), "-m", data, "-t", str(mqtt_status_topic), "-i", "C2C_Subscription", "-r"])

def mqtt_get_value():
    data=rest()
    for i in data:
        mqtt_status_topic=(i['mqtt_status_topic'])
    b_mqtt(mqtt_status_topic,data)
    
def parse_response(data):
    chronothermostats_stored=load_api_config_arg("chronothermostats")
    for j in json.loads(data):
        try:
           c2c_response=(j['data'])
           for c in chronothermostats_stored:
               topology=c['chronothermostat']['topology']
               name=c['chronothermostat']['name']
               mqtt_status_topic=c['chronothermostat']['mqtt_status_topic']
               for chronothermostat in c2c_response['chronothermostats']:
                   if topology == chronothermostat['sender']['plant']['module']['id']:
                      function=(chronothermostat['function'])
                      mode=(chronothermostat['mode'])
                      state=(chronothermostat['loadState'])
                      setpoint=(chronothermostat['setPoint']['value'])
                      remaining_time=None
                      remaining_time_minutes=None
                      try:
                          activationTime=(chronothermostat['activationTime'])
                          date2=(datetime.datetime.strptime(activationTime, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now())
                          remaining_time_minutes = str(date2.total_seconds() / 60).split(".")[0]
                          remaining_time="h e ".join(str(datetime.datetime.strptime(activationTime, "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now()).split(".")[0].split(":", 2)[:2])+"m"
                          if "0h e" in remaining_time:
                             remaining_time=remaining_time.split("0h e ")[1]
                      except:
                          pass
                      programs=(chronothermostat['programs'])
                      for prog in programs:
                          program_number = prog['number']
                          program_name = get_programs_name_from_local(topology, program_number)
                      thermometers=(chronothermostat['thermometer']['measures'])
                      for thermometer in thermometers:
                          temperature = thermometer['value']
                      hygrometers=(chronothermostat['hygrometer']['measures'])
                      for hygrometer in hygrometers:
                          humidity = hygrometer['value']
                      mqtt_data = json.dumps({ "name": name, "mode" : mode, "function" : function ,  "state" : state, "setpoint" : setpoint, "temperature" : temperature, "humidity" : humidity, "program": program_name, "remaining_time": remaining_time, "remaining_time_minutes": remaining_time_minutes})
                      b_mqtt(mqtt_status_topic,mqtt_data)
        except:
           name = (j['name'])
           mode = (j['mode'])
           function = (j['function'])
           state = (j['state'])
           setpoint = (j['setpoint'])
           temperature = (j['temperature'])
           humidity = (j['humidity'])
           mqtt_status_topic = (j['mqtt_status_topic'])
           mqtt_data = json.dumps({ "name": name, "mode" : mode, "function" : function ,  "state" : state, "setpoint" : setpoint, "temperature" : temperature, "humidity" : humidity })
           b_mqtt(mqtt_status_topic,mqtt_data)

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    if request.method == 'POST':
       parse_response(request.data)
       return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    else:
        code = request.args.get('code')
        access_token, refresh_token = get_access_token(code)
        if access_token != None and refresh_token != None:
           my_plants=get_plants(access_token)
           chronothermostats=get_topology(access_token,my_plants)
           update_api_config_file_code(code)
           update_api_config_file_access_token(access_token)
           update_api_config_file_refresh_token(refresh_token)
           update_api_config_file_my_plants(my_plants)
           update_api_config_file_chronothermostats(chronothermostats)
           if check_config_file():
              shutil.move(os.path.join(tmp_api_config_file), os.path.join(static_api_config_file))
           check_config_file()
           my_value_tamplate=rest()
           return render_template('info.html', j_response=my_value_tamplate)
        else:
           return "something went wrong"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5588)
