from confluent_kafka import Consumer, KafkaException, KafkaError
from pymongo import MongoClient
import requests
import json

# MongoDB setup
client = MongoClient("mongodb://mongo_data:27017")
db = client["f1_data"]
collection = db["new_data"]
# from confluent_kafka import Consumer, KafkaError



def make_request(driver_number, session_key): 
    url = f"https://api.openf1.org/v1/car_data?session_key={session_key}&driver_number={driver_number}"
    try:
        response_data = requests.get(url).json()
        print("collected data for : ", driver_number," for session: ",  session_key, flush = True)
        return response_data
    except Exception as e:
        print("error while makig request: ", e,flush=True )
        return []

def consume_messages(bootstrap_servers, group_id, topic_name):
    consumer = Consumer({
        'bootstrap.servers': bootstrap_servers,  # Kafka broker
        'group.id': group_id,    # Consumer group ID
        'auto.offset.reset': 'earliest',    # Start consuming from earliest offset
        'enable.auto.commit': False         # Disable auto-commit for better control
    })
    consumer.subscribe([topic_name])
    print("subscirbed to : ", topic_name)
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition
                    continue
                else:
                    # Handle other errors
                    print(msg.error())
                    break

            # Print the received message value
            print('Received message: {}'.format(msg.value().decode('utf-8')), flush=True)
            message = json.loads(msg.value().decode('utf-8'))
            data = make_request(message["driver_number"], message["session_key"])
            print("obtained these data: ", data, flush=True)
            try:
                collection.insert_many(data)
                print("data stored in mongo")
            except Exception as e:
                print("error while storing data: ", e)
            # print(collection.insert_one({"newdatainserted":"test"}))


    finally:
        # Close the consumer
        consumer.close()

bootstrap_servers = 'kafka:9092'
group_id = 'f1_consumer_group'
topic_name = 'data_topic'
print("ready for consuming messages")
consume_messages(bootstrap_servers, group_id, topic_name)



# from kafka import KafkaConsumer
# from pymongo import MongoClient
# import requests
# import json

# # Kafka Consumer setup
# consumer = KafkaConsumer(
    
#     bootstrap_servers='kafka:9092',
#     auto_offset_reset='earliest',
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )

# # MongoDB setup
# client = MongoClient("mongodb://mongo_data:27017")
# db = client["f1_data"]
# collection = db["car_data"]

# # Function to fetch API data
# def fetch_api_data(record):
#     session_key = record["session_key"]
#     driver_number = record["driver_number"]
#     print("fetching for this session: ", session_key)
#     url = f"https://api.openf1.org/v1/car_data?session_key={session_key}&driver_number={driver_number}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {}
# consumer.subscribe(["number_and_session"])
# # Consume messages and process API calls
# for message in consumer:
#     record = message.value
#     print("recived from producer: ",record)
#     api_response = fetch_api_data(record)
#     if api_response:
#         collection.insert_many(api_response)  # Save API response to MongoDB
#         print(f"Processed record: {record}")
