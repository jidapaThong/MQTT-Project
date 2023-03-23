# CPE314-MQTT-Project

This is a project in course CPE314 Computer Networks, for the first half of the semester, implementing the IOT communication using MQTT protocol.

## Table of Contents
- [Documentation](#documentation)
- [Installation](#installation)
- [Getting Started](#getting-started)

## Documentation

There are total of 3 files in this project, ["publisher.py](publisher.py)", "[subscriber.py](./subscriber.py)", and "[surrealdb.py](./surrealdb.py)" 
this project assumes the usage of local broker with port number 1883, and alognside with
[SurrealDB](https://surrealdb.com/) as database for the server through local address with port 8000. And the data using 
as the sample data exchanging to each other is "SampleInput.xlsx".

The topic that is used in this project are "nodes/$publisher-id/sensors/$sensor-type/$time"
with extension of "/batches/$batch-number" where only thermal array will be using batches number.

The "[SampleInput.xlsx](./SampleInput.xlsx)" is the sample input to used as a node information sent out from the node
with time interval to the broker.

The "[publisher.py](./publisher.py)" is the python file containing the code for publisher to read the sample
input and published it through the connected broker through specified topic.

The broker is the local broker with port 1883 as port number used to communicate
between each other.

The "[subscriber.py](./subscriber.py)" is the python file containing the code for subscriber to received the message
from broker and write the data to the database.

The "[surrealdb.py](./surrealdb.py)" is the python file containing the code for python client for the SurrealDB
database which it commnunicate throgh local host with port number 8000.

The "[requirements.txt](./requirements.txt)" is the file containing the name and version of the required packages
used to run the project.

## Installation

To install this project requirements, run
```
pip install -r requirements.txt
```

As for the broker, you can download and use the [Mosquitto](https://mosquitto.org/download/).

As for the database, you can download it through the [SurrealDB](https://surrealdb.com/docs/start/installation) website in installation page.

## Getting Started

To start the database for the docker, run
```
docker run --rm -p 8000:8000 surrealdb/surrealdb:latest start --log debug --user root --pass root memory
```

To start the broker, run
```
mosquitto -v
```

To start the subscriber, run
```
python subscriber.py -n client-id -sl subscribe-list
```
where "client-id" is the id of the subscriber, and subscribe-list is a list of publisher id that
we want to subscribe.

To start the publisher, run
```
python publisher.py -n client-id
```
where "client-id" is the id of the publisher.