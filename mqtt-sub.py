import paho.mqtt.client as mqtt #import the client
import sys
# Function to process recieved message


if len(sys.argv)!=2:
    print("Please specify name of the file to store incoming data")
    print('Usage: python mqtt-sub.py file-name.csv')
    sys.exit()

dataFile=open(sys.argv[1],"w")


def process_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("message received " ,msg)
    print("message topic=",message.topic)
    topics = (message.topic).split('/')
    dataFile.write(topics[1]+","+msg)
    print('Writing to file')


# Create client
client = mqtt.Client("subsciber-1")

# Assign callback function
client.on_message = process_message

# Connect to broker
client.connect("127.0.0.1",1883,60)

# Subscriber to topic
client.subscribe("respeaker/+")

# Run loop
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Closing data file...")
    dataFile.close()
    print('Disconnecting to broker')
    client.disconnect()
