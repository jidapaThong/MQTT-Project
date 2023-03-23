from paho.mqtt import client as mqtt
from argparse import ArgumentParser
import sys
from surrealdb import db
import json

#
# Parse command line argument section
# use -n, or ---name to specify the client id
# use -sl, or --subscribe-list to specify the subscriber id to subscribe to
#
parser = ArgumentParser()
parser.add_argument("-n", "--name", dest="client_id")
parser.add_argument("-sl", "--subscribe-list", dest="subscribes_id", nargs="+")
args = parser.parse_args()

#
# Define constant use by the program
#
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "Test-Topic"
MQTT_HUMIDITY_TOPIC = "nodes/node-id/sensors/humidity/#"
MQTT_TEMPERATURE_TOPIC = "nodes/node-id/sensors/temperature/#"
MQTT_THERMAL_ARRAY_TOPIC = "nodes/node-id/sensors/thermal/+/batches/#"
MQTT_USERNAME = "cpe314-project-username"
MQTT_PASSWORD = "cpe314-project-password"

MQTT_CLIENT = "Test-Subcriber" if args.client_id == None else args.client_id

#
# Define functions used in the program
#

# on connection call back function used by client
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with resulted code "+str(rc))
    else:
        exit(1)

# on message incoming from broker
# print out the information about incoming message
# and call appropriate function to handle for each type
def on_message(client, userdata, msg):
    topic_paths = msg.topic.split('/')
    subscriber_id = topic_paths[1]
    sensor_type = topic_paths[3]
    time = topic_paths[4].replace(" ", "T") + "Z"
    print("client: "+subscriber_id+" | topic: "+msg.topic+" | payload: "+str(msg.payload.decode('utf-8'))+" | size: "+str(sys.getsizeof(msg.payload)))
    if sensor_type == "humidity":
        on_sensor_humidity(subscriber_id, time, str(msg.payload.decode('utf-8')))
    elif sensor_type == "temperature":
        on_sensor_temperature(subscriber_id, time, str(msg.payload.decode('utf-8')))
    elif sensor_type == "thermal":
        on_sensor_thermal_array(subscriber_id, time, topic_paths[-1], msg.payload.decode('utf-8').split(',')[:-1])

# on message received is from humidity sensor
# print out the value of received information about humidity
# and insert that information to database
def on_sensor_humidity(publisher_id, time, humidity):
    print(f"client: {publisher_id} | time: {time} | humidity: {humidity}")

    table = MQTT_CLIENT
    
    db_response = db(f"""
        LET $id="publishers/{publisher_id}/times/{time}";
        LET $publisher="{publisher_id}";
        LET $time="{time}";
        LET $humidity={humidity};
        INSERT INTO `{table}` (id, publisher, time, humidity)
        VALUES ($id, $publisher, $time, $humidity)
        ON DUPLICATE KEY UPDATE humidity=$humidity;
    """)

# on message received is from temperature sensor
# print out the value of received information about temperature
# and insert that information to database
def on_sensor_temperature(publisher_id, time, temperature):
    print(f"client: {publisher_id} | time: {time} | temperature: {temperature}")

    table = MQTT_CLIENT

    db_response = db(f"""
        LET $id="publishers/{publisher_id}/times/{time}";
        LET $publisher="{publisher_id}";
        LET $time="{time}";
        LET $temperature={temperature};
        INSERT INTO `{table}` (id, publisher, time, temperature)
        VALUES ($id, $publisher, $time, $temperature)
        ON DUPLICATE KEY UPDATE temperature=$temperature;
    """)

# on message received is from temperature sensor
# print out the value of received information about temperature
# query for existing thermal array, then append the received thermal array
# then inset new thermal array into the database
def on_sensor_thermal_array(publisher_id, time, batch_number, thermal_array):
    print(f"client: {publisher_id} | time: {time} | batch: {batch_number} | payload: {thermal_array}")

    table = MQTT_CLIENT
    id = f"publishers/{publisher_id}/times/{time}"

    db_response = db(f"""
        LET $id="publishers/{publisher_id}/times/{time}";
        LET $publisher="{publisher_id}";
        LET $time="{time}";
        LET $thermal=[{thermal_array}];
        SELECT thermal FROM {table}:`{id}`;
    """)

    prev_thermal_array = db_response[4]["result"][0]["thermal"]
    if prev_thermal_array == None:
        prev_thermal_array = []
    new_thermal_array = prev_thermal_array + thermal_array
    db_response = db(f"""
        LET $id="publishers/{publisher_id}/times/{time}";
        LET $publisher="{publisher_id}";
        LET $time="{time}";
        LET $thermal={new_thermal_array};
        INSERT INTO `{table}` (id, publisher, time, thermal)
        VALUES ($id, $publisher, $time, $thermal)
        ON DUPLICATE KEY UPDATE thermal=$thermal;
    """)
    

# initialize client
client = mqtt.Client(MQTT_CLIENT)
client.on_connect = on_connect
client.on_message = on_message

# connect client to specified broker ip, port, and keep alive time
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# loop to retrive the subscribe id of subscribed node,
# then subscribe to each node for each sensor type
for key, value in args._get_kwargs():
    if key == "subscribes_id":
        for subscribe_id in value:
            client.subscribe(MQTT_HUMIDITY_TOPIC.replace('node-id', subscribe_id))
            client.subscribe(MQTT_TEMPERATURE_TOPIC.replace('node-id', subscribe_id))
            client.subscribe(MQTT_THERMAL_ARRAY_TOPIC.replace('node-id', subscribe_id))

# loop to continuously listening for incoming messages
client.loop_forever()