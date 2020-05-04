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

from Adafruit_IO import *
username = "insert Adafruit_IO username"
activeKey = "insert Adafruit_IO active key"
aio = Client("insert Adafruit_IO username","insert Adafruit_IO active key") #UserID & KEY


host          = "node02.myqtthub.com"
port          = 1883
clean_session = True
client_id     = "set client id from client.json"
user_name     = "insert myqtthub username"
password      = "insert myqtthub password"
clientLoop = []

    


class TempProbe:
    def __init__(self, name):
        self.name = name
        self.timeover = 0
    
    #this doesnt run for some reason
    def inctime(self):
        self.timeover+=1
        
    def gettime(self):
        return self.timeover
    
    def getname(self):
        return self.name
    
    def resettime(self):
        self.timeover = 0
    
    def action(self, jsonStr, obj):
        print("Raw JSON: %s" % jsonStr)
        observation = json.loads(jsonStr)
        temp = float(observation[obj.name])
        if temp > 50: #set this to max temp(C) limit to 50C 
            print("Temp is over limit: %s" % temp)
            self.inctime()
            print("Increment Time to %s" % self.gettime())
            if self.gettime() > 40: #timelimit(in mins) * 60 / loop gap(in seconds) = (10*60/15)
                #client.publish ("some/message/to/publish", '{"%s" : "Warning"}' % obj.name)
                
                warningCode = 1
                key = str(obj.name)
                # change the 'pressure' parameter to match the key for your pressure feed.
                aio.send(key, warningCode)
                
                print("Waring Sent!")
                self.resettime()
        else:
            self.resettime()
            print("Temp Good!")


class creation:
    def __init__(self):
        self.clientarray = []
        
    def createobjects(self):
        with open('clients.json', 'r') as myfile:
            data=myfile.read()
        clientjson = json.loads(data)
        self.clientarray = clientjson['clients']
    
        for i in self.clientarray:
            clientLoop.append(TempProbe(i))
             
        for obj in clientLoop:
            print(obj.name)
    
    def readdevices(self, msg):
        
        for obj in clientLoop:
            print(obj.name)
            try:
                obj.action(msg, obj)
            except:
                print("Wrong Node!")
    
creator = creation()

def on_connect (client, userdata, flags, rc):
    """ Callback called when connection/reconnection is detected """
    print("Connect %s result is: %s" % (host, rc))
    client.subscribe("some/message/to/publish")
    print("User Nodes:")
    creator.createobjects()
    
    # With Paho, always subscribe at on_connect (if you want to
    # subscribe) to ensure you resubscribe if connection is
    # lost.
    # client.subscribe("some/topic")

    if rc == 0:
        client.connected_flag = True
        print("Connection good!")
        return
    
    print("Failed to connect to %s, error was, rc=%s" % rc)
    # handle error here
    sys.exit (-1)


def on_message(client, userdata, msg):
    jsonStr = str(msg.payload.decode("UTF-8"))
    creator.readdevices(jsonStr)
    
# Define clientId, host, user and password
client = mqtt.Client (client_id = client_id, clean_session = clean_session)
client.username_pw_set (user_name, password)

client.on_connect = on_connect
client.on_message = on_message

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
        factor = 3
        
        # temp_calc is accurate to +/- 2 deg C.
        temp_calc = ((p+h)/2) - (c/factor)
        
        #temp = temp_calc
        temp = temp_calc
        
        client.publish ("some/message/to/publish", '{"%s" : "%s"}' % (client_id, temp))
        
        client.loop ()
    except Exception:
        print("error")
    time.sleep(15) #gap between publish 15

print("Publish operation finished with ret=%s" % ret)

# close connection
client.disconnect ()