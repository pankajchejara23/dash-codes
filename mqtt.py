import paho.mqtt.client as mqtt

#  function
def connect_msg():
    print('Connected to Broker')

# function
def publish_msg():
    print('Message Published')

# Creating client
client = mqtt.Client(client_id='publisher-1')

# Connecting callback functions
client.on_connect = connect_msg
client.on_publish = publish_msg

# Connect to broker
client.connect("127.0.0.1",1883)

# Publish a message with topic
ret= client.publish("house/light","on")

# Run a loop
client.loop()
