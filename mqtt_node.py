import paho.mqtt.client as mqtt
import time
import ssl
import json

from sense_hat import SenseHat
sense = SenseHat()

from cpu_temp import CPUTemp
cput = CPUTemp()
cput.__init__()
cput.open()


host          = "node02.myqtthub.com"
port          = 1883
clean_session = True
client_id     = "set client id from client.json"
user_name     = "insert myqtthub username"
password      = "insert myqtthub password"

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print ("Connect %s result is: %s" % (host, rc))
    client.subscribe("some/message/to/publish")
    #creator.createobjects()
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
    # client.subscribe("some/topic")

    if rc == 0:
        client.connected_flag = True
        print ("Connection good!")
        return
    
    print ("Failed to connect to %s, error was, rc=%s" % rc)
    # handle error here
    sys.exit (-1)


# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect

# configure TLS connection
# client.tls_set (cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
# client.tls_insecure_set (False)
# port = 8883

# connect using standard unsecure MQTT with keepalive to 60
client.connect (host, port, keepalive = 60)
client.connected_flag = False
while not client.connected_flag:           #wait in loop
    client.loop()
    time.sleep (1)

# publish message (optionally configuring qos=1, qos=2 and retain=True/client.loop ()
while True:
    try:
        #get cpu temperature
        c = cput.get_temperature()
        
        #get temperature and humidity from sensehat
        p = sense.get_temperature_from_pressure()
        h = sense.get_temperature_from_humidity()
        
        # factor = 3 appears to work if the RPi is in a case
        # change to factor = 5 appears to work for RPi's not in a case
        factor = 5
        
        # temp_calc is accurate to +/- 2 deg C.
        temp_calc = ((p+h)/2) - (c/factor)
        
        #temp = temp_calc
        temp = temp_calc
        
        client.publish ("some/message/to/publish", '{"%s" : "%s"}' % (client_id, temp))
        print('Output: {"%s" : "%s"}' % (client_id, temp))
        client.loop ()
    except Exception:
        print("error")
    time.sleep(15)

print ("Publish operation finished with ret=%s" % ret)

# close connection
client.disconnect ()