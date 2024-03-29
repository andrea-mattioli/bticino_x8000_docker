# Bticino Home Assistant Integration
Chronothermostat Bticino X8000 Integration

### CLICK ON REBUILD AFTER ADD-ON UPGRADE and on app https://ip:5588 click ***get your code***

[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)

[![Sponsor Mattiols via GitHub Sponsors](https://raw.githubusercontent.com/andrea-mattioli/bticino_X8000_rest_api/test/screenshots/sponsor.png)](https://github.com/sponsors/andrea-mattioli)

🍻 [![Sponsor Mattiols via paypal](https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg)](http://paypal.me/mattiols)

### Italian support: [![fully supported](https://raw.githubusercontent.com/andrea-mattioli/bticino_X8000_rest_api/test/screenshots/telegram_logo.png)](https://t.me/HassioHelp)

## 1. First step

### 1.1. Register a Developer account
Sign up for a new Developer account on Works with Legrand website (https://developer.legrand.com/login).

### 1.2. Subscribe to Legrand APIs
Sign in, go to menu "API > Subscriptions" and make sure you have "Starter Kit for Legrand APIs" subscription activated; if not, activate it.

![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/subscription.PNG?raw=true "App Register")

### 1.3. Register a new application
Go to menu "User > My Applications" and click on "Create new" to register a new application:
- Insert a **valid public URL** in "First Reply Url". 
- Make sure to tick the checkbox near scopes `comfort.read` and `comfort.write`

Submit your request and wait for a response via email from Legrand (it usually takes 1-2 days max).
If your app has been approved, you should find in the email your "Client ID" and "Client Secret" attributes.

```
Public Url = https://myDomain:5588/
```
```
First Reply Url = https://myDomain:5588/callback
```
![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/app1.png?raw=true "App Register")
![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/app2.png?raw=true "App Register")

## 2. CONFIGURATION

### 2.1. Start Docker Container

Update the bash script variable with your correct data:
```
#! /bin/bash
ARCH=$(uname -m)
## edit variable with your value
CLIENT_ID="recived via email"
CLIENT_SECRET="recived via email"
SUBSCRIPTION_KEY="subscription key"
DOMAIN="my home domain example.com"
API_USER="chose your api user"
API_PASS="chose your api password"
MQTT_BROKER="ip broker"
MQTT_PORT=1883
MQTT_USER="your mqtt user"
MQTT_PASS="your mqtt password"
USE_SSL="True/False"
### start container
docker run -t -i -e TZ='Europe/Rome' \
-e CLIENT_ID='${CLIENT_ID}' \
-e CLIENT_SECRET='${CLIENT_SECRET}' \
-e SUBSCRIPTION_KEY='${SUBSCRIPTION_KEY}' \
-e DOMAIN='${DOMAIN}' \
-e HAIP='${HAIP}' \
-e MQTT_BROKER='${MQTT_BROKER}' \
-e MQTT_PORT='1883' \
-e MQTT_USER='${MQTT_USER}' \
-e MQTT_PASS='${MQTT_PASS}' \
-e USE_SSL='${USE_SSL}' \
-p 5588:5588 \
--name ha_bticino_x_8000 amattioli2/homeassistant_addon_bticino_x_8000:${ARCH}
```
### 2.2. Nat API port: "80,5588" on your router/firewall 
If you use "use_ssl: true" and you have already a valid ssl certificate installed in your hassio env, you can open only 5588 on your router, but if you want a new certificate you must open http port 80!
Else if you use Nginx proxy manager use "use_ssl: false" and proxy bticino_smarter app with nginx!
## 3. START

### 3.1. 1st RUN
- Navigate to {http/https}://my_hassio_ip:5588/ and click ***get your code***

![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/api1.png?raw=true "Api Allow")

- **Login with your developer account**


![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/api2.png?raw=true "Api Allow")

- **Allow your app permissions**


![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/api3.png?raw=true "Api Allow")

- **If you see your Plant Info enjoy!!**


![Alt text](https://github.com/andrea-mattioli/bticino_X8000_rest_api/raw/test/screenshots/app1.PNG?raw=true "Api Allow")

- **FOR CUSTOMIZATION MQTT command payload**
```
topic command: /bticino/{id}/cmd
topic callback: /bticino/{id}/status
PAYLOAD: 
  AUTOMATIC
  MANUAL
  HEATING
  COOLING
  OFF
  OFF (integer)m
  OFF (integer)h
  OFF (integer)d
  PROTECTION
  BOOST-30
  BOOST-60
  BOOST-90
  (number)
  (number) (integer)m
  (number) (integer)h
  (number) (integer)d
  ProgramName (string)

example:
    AUTOMATIC --> set thermostat mode to automatic
    MANUAL --> set thermostat mode to manual
    BOOST-30 --> set thermostat mode to boost for 30 minutes
    BOOST-60 --> set thermostat mode to boost for 60 minutes
    BOOST-90 --> set thermostat mode to boost for 90 minutes
    HEATING --> set thermostat function to heat
    COOLING --> set thermostat function to cool
    20 --> set thermostat temperature at 20 C° in maual mode forever
    18 --> set thermostat temperature at 18 C° in maual mode forever
    21.5 --> set thermostat temperature at 21.5 C° in maual mode forever
    20 5m --> set thermostat temperature at 20 C° in maual mode for 5 minutes
    20 1h --> set thermostat temperature at 20 C° in maual mode for 1 hour
    20 1d --> set thermostat temperature at 20 C° in maual mode for 1 day
    OFF --> turn off thermostat forever
    OFF 5m --> turn off thermostat for 5 minutes
    OFF 3h --> turn off thermostat for 3 hours
    OFF 2d --> turn off thermostat for 2 day
    PROTECTION --> set thermostat mode to protection forever
    At Home --> set thermostat program to "At Home"
```
change the state_topic and cmd_topic for each thermostat


