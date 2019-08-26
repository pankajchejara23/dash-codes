import paho.mqtt.client as mqtt
import datetime
#  function
def connect_msg():
    print('Connected to Broker')

# function
def publish_msg():
    print('Message Published')

# Creating client
client = mqtt.Client(client_id='publish1')

# Connecting callback functions
client.on_connect = connect_msg
client.on_publish = publish_msg

# Connect to broker
client.connect("127.0.0.1",1883,60)

# Publish a message with topic
for d in [60,59,150,331,210]:
    data = str(datetime.datetime.now())+", %d\n"%d
    ret= client.publish("respeaker/+",data)

# Run a loop
try:
    client.loop_forever()
except KeyboardInterrupt:

    client.disconnect()
