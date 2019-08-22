import paho.mqtt.client as mqtt #import the client

# Function to process recieved message
def process_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)



# Create client
client = mqtt.Client("subsciber-1")

# Assign callback function
client.on_message = process_message

# Connect to broker
client.connect("127.0.0.1",1883,60)

# Subscriber to topic
client.subscribe("respeaker/group-1")

# Run loop
client.loop_forever()
