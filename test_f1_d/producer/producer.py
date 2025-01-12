# from kafka import KafkaProducer
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer
import json

# Kafka configuration
conf = {'bootstrap.servers': 'kafka:9092', 'acks': 'all'}

def create_topic(topic_name):
    admin_client = AdminClient(conf)
    if topic_name in admin_client.list_topics().topics:
        print(f"Topic '{topic_name}' already exists.")
        return
    topic = NewTopic(topic_name, num_partitions=3, replication_factor=1)
    try:
        futures = admin_client.create_topics([topic])
        for topic, future in futures.items():
            try:
                future.result()  # Wait for topic creation
                print(f"Topic '{topic}' created successfully.")
            except Exception as e:
                print(f"Failed to create topic '{topic}': {e}")
    except Exception as e:
        print(f"Admin client error: {e}")

def check_kafka_status():
    admin_client = AdminClient(conf)
    return list(admin_client.list_topics(timeout=10).topics.keys())

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record successfully delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Data to send
object_to_send = [
    {'driver_number': 16, 'team_name': 'Ferrari', 'full_name': 'Charles LECLERC', 'name_acronym': 'LEC', 'session_key': 9153, 'circuit_short_name': 'Monza', 'session_name': 'Qualifying'},
    {'driver_number': 16, 'team_name': 'Ferrari', 'full_name': 'Charles LECLERC', 'name_acronym': 'LEC', 'session_key': 9157, 'circuit_short_name': 'Monza', 'session_name': 'Race'},
    {'driver_number': 16, 'team_name': 'Ferrari', 'full_name': 'Charles LECLERC', 'name_acronym': 'LEC', 'session_key': 9511, 'circuit_short_name': 'Imola', 'session_name': 'Qualifying'}
]

# Create a new topic
topic_name = "data_topic"
create_topic(topic_name)

# Check existing topics
topics = check_kafka_status()
print("Existing topics:", topics)

# Initialize the producer
p = Producer(conf)

# Produce messages to Kafka
for driver in object_to_send:
    key = str(driver["driver_number"]).encode('utf-8')  # Ensure key is in bytes
    value = json.dumps(driver)  # Convert dictionary to JSON string
    p.produce(
        topic_name,
        key=key,
        value=value,
        on_delivery=delivery_report
    )

# Flush to make sure all messages are sent
p.flush()

# spark = SparkSession.builder \
#     .appName("API to MongoDB Multi-Endpoint") \
#      .config('spark.ui.port', '4040') \
#     .config("spark.jars.packages", 'org.mongodb.spark:mongo-spark-connector_2.12:10.3.0') \
#     .config("spark.mongodb.connection.uri", "mongodb://mongo_data:27017/f1_data") \
#     .getOrCreate()


# # # Load data from collection1
# circuits_info = spark.read.format("mongodb") \
#     .option("database", "f1_data") \
#     .option("collection", "circuits_info") \
#     .load()

# # Load data from collection2
# drivers_data = spark.read.format("mongodb") \
#     .option("database", "f1_data") \
#     .option("collection", "drivers") \
#     .load()



# Kafka Producer setup
# producer = KafkaProducer(
#     bootstrap_servers='kafka:9092',
#     value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize data to JSON
# )
# _sess_keys = circuits_info.select(col("session_key"), col("circuit_short_name"), col("session_name")).rdd
# _driv_nmub = drivers_data.select(col("driver_number"),col("team_name"),col("full_name"),col("name_acronym")).rdd


# Generate Cartesian product
# combined_rdd = _sess_keys.cartesian(_driv_nmub).map(
#     lambda pair: {**pair[0].asDict(), **pair[1].asDict()}
# )

# Send each pair to Kafka
# def send_to_kafka(record):
#     print("sending this record form producer: ", record)
#     producer.send("number_and_session", record)


# combined_rdd = spark.sparkContext.parallelize(object_to_send)
# print("obtained object with this partition", combined_rdd.getNumPartitions())
# combined_rdd.foreach(send_to_kafka)

# for driver in object_to_send:
#     send_to_kafka(driver)
# producer.flush()
# producer.close()
# print("Messages sent to Kafka!")
# spark.stop()