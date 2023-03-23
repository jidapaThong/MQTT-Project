from paho.mqtt import client as mqtt
from argparse import ArgumentParser
import openpyxl
import textwrap
import time

#
# Parse command line argument section
# use -n, or ---name to specify the client id
#
parser = ArgumentParser()
parser.add_argument("-n", "--name", dest="client_id")
args = parser.parse_args()

#
# Define constant use by the program
#
UTF_8_MAX_BYTES_PER_CHAR = 3  # number of max-bytes ut-8 character
# max number of bytes constraint specified by instruction, reduce to 240 easire divide by 3
MQTT_MAX_BYTES = 240
MQTT_CHAR_PER_ARR = 5

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "Test-Topic"
MQTT_HUMIDITY_TOPIC = "nodes/+/sensors/humidity"
MQTT_TEMPERATURE_TOPIC = "nodes/+/sensors/temperature"
MQTT_THERMAL_ARRAY_TOPIC = "nodes/+/sensors/thermal"
MQTT_THERMAL_ARRAY_BATCH_SIZE = MQTT_CHAR_PER_ARR * 16
MQTT_USERNAME = "cpe314-project-username"
MQTT_PASSWORD = "cpe314-project-password"

MQTT_CLIENT = "Test-Publisher" if args.client_id == None else args.client_id

#
# Define functions used in the program
#

# read excel by using openxl library, and return the active worksheet
def read_excel():
    workbook = openpyxl.load_workbook("SampleInput.xlsx")
    worksheet = workbook.active
    return worksheet

# get column name array from the top worksheet
def get_columns_name(worksheet):
    columns_name = []
    for cell in worksheet[1]:
        columns_name.append(cell.value)
    return columns_name

# on connection call back function used by client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with resulted code "+str(rc))
    else:
        exit(1)

#
# Set up client for paho-mqtt, specify client id, on connect callback,
# and connect the client to broker 
#

# initialize client
client = mqtt.Client(MQTT_CLIENT)
client.on_connect = on_connect

# connect client to specified broker ip, port, and keep alive time
client.connect(MQTT_BROKER, MQTT_PORT, 60)

#
# Read example excel, and get column names for each column
#
worksheet = read_excel()
columns_name = get_columns_name(worksheet)

#
# Loop in worksheet, for each row, send publish humidity, temperature,
# and batch of thermal array
#
for row in worksheet.iter_rows(values_only=True, min_row=2):
    mqtt_topic_humidity = MQTT_HUMIDITY_TOPIC.replace(
        '+', MQTT_CLIENT) + '/' + str(row[0]) # format topic for humidity ex. "/nodes/+pub1/sensors/humidity/#time"
    mqtt_topic_temperature = MQTT_TEMPERATURE_TOPIC.replace(
        '+', MQTT_CLIENT) + '/' + str(row[0]) # format topic for humidity ex. "/nodes/+pub1/sensors/temperature/#time"
    #print(mqtt_topic_humidity)
    #print(mqtt_topic_temperature)

    client.publish(mqtt_topic_humidity, str(row[1]))
    client.publish(mqtt_topic_temperature, str(row[2]))

    thermals_string = textwrap.wrap(row[3], MQTT_THERMAL_ARRAY_BATCH_SIZE) # split thermal array into batches
    #
    # for each batch of thermal array, publish it one by one to broker
    #
    for jdx, thermal in enumerate(thermals_string):
        mqtt_topic_thermal = MQTT_THERMAL_ARRAY_TOPIC.replace(
            '+', MQTT_CLIENT) + '/' + str(row[0]) + '/batches/' + str(jdx) # format topic for thermal array ex. "/nodes/+pub1/sensors/thermal/#time/batches/1"
        #print(mqtt_topic_thermal)

        client.publish(mqtt_topic_thermal, str(thermal))
    time.sleep(1) # sleep to prevent heavy load in each row of publishing

# client.loop_forever()
