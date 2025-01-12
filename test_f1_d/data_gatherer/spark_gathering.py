from pyspark import SparkContext, SparkConf
import fastf1
from pymongo import MongoClient
from datetime import datetime, date
import pandas as pd
# Function that sums the elements in a partition
# def sum_partition(partition):
#     yield sum(partition)

# Initialize Spark context with a local mode setup
def get_drivers(year, round_number,circuit_name):
    print("getting drivers for ", circuit_name)
        # Recupera la sessione di gara
    fastf1.Cache.enable_cache('/opt/bitnami/python/cache')
 
    session = fastf1.get_session(year, round_number, 'R')  
    
    # per sprint race: 
    try:
        sprint_race = fastf1.get_session(year, round_number, 'Sprint')
        sprint_race.load(telemetry=False, laps=False, weather=False, messages=False)
        sprint_results = sprint_race.results
        sprint_results = sprint_results[['Abbreviation', 'FullName', 'TeamName', 'GridPosition', 'Position', 'ClassifiedPosition', 'Points']].drop_duplicates()
        sprint_results["Session"] = "Sprint"
    except ValueError:
        print(f"no sprint races for {year} round : {round_number}")
        sprint_results = pd.DataFrame({})

    # Carica i dati della sessione
    session.load(telemetry=False, laps=False, weather=False, messages=False)
    # Ottieni i risultati della gara
    results = session.results
    
 
    # Estrai le informazioni per ogni pilota 
    driver_info = results[['Abbreviation', 'FullName', 'TeamName', 'GridPosition', 'Position', 'ClassifiedPosition', 'Points']].drop_duplicates()
    driver_info["Session"] = "Race"
    # Estrai il nome del circuito
    circuit_name = session.event['EventName']  # Nome completo dell'evento, come "Bahrain Grand Prix"
    
    full_data_to_store = pd.concat([driver_info,sprint_results],axis=0,ignore_index = True)
    # Aggiungi il nome del circuito come nuova colonna
    driver_info['Circuit'] = circuit_name
    records_to_save = [{
                "Round": round_number,
                "Event_Name": circuit_name,  # Nome del Gran Premio
                "Abbreviation": record.Abbreviation,  # Nome del circuito
                "FullName": record.FullName,
                "TeamName":record.TeamName,
                "GridPosition":record.GridPosition,
                "Position" : record.Position,
                "ClassifiedPosition":record.ClassifiedPosition,
                "Points" : record.Points,
                "Year"    : year,
                "Session" : record.Session
            }for idx,record in full_data_to_store.iterrows()]
    try:
        drivers_collection.insert_many(records_to_save)
    except Exception  as e:
        print("error while connetcing to mongo", e)
    # return driver_info
 
# # Esempio d'uso: estrai i piloti per il Gran Premio del Bahrain 2023 (round 1)
# drivers_bahrain_2023 = get_drivers_with_teams(2023, 1)
# print(drivers_bahrain_2023)
 


def main():
    
       # Configure Spark (local mode)
    # conf = SparkConf().setAppName("MapPartitionsExample").setMaster("local[*]")
    # sc = SparkContext(conf=conf)

    # # Create an RDD with some data
    # data = list(range(1, 101))  # A simple list of numbers from 1 to 100
    # rdd = sc.parallelize(data, 5)  # Distribute data into 5 partitions

    # # Use mapPartitions to sum each partition
    # partition_sums = rdd.mapPartitions(sum_partition).collect()

    # # Print the sums of each partition
    # print("Sum of elements in each partition:")
    # print(partition_sums)

    year1 = 2023
    circuit_list_2023 = []
 
    # Loop su tutti i round del campionato (22 round per il 2023)
    for round_number in range(1, 23):  
        try:
            event = fastf1.get_event(year1, round_number)  # Recupera l'evento
            record = {
                "Round": round_number,
                "Nome GP": event.EventName,  # Nome del Gran Premio
                "Circuito": event.Location,  # Nome del circuito
                "Data": year1 # Data dell'evento
            }

            # if isinstance(record["Data"], date):
            #     record["Data"] = datetime.combine(record["Data"], datetime.min.time())
            
            circuit_list_2023.append(record)
        
        except Exception as e:
            print(f"Errore nel caricare il round {round_number}: {e}")
    # collection.insert_many(circuit_list_2023)
    # Stampa l'elenco dei circuiti
    # for circuit in circuit_list_2023:
    #     print(f"Round {circuit['Round']}: {circuit['Nome GP']} - {circuit['Circuito']} ({circuit['Data']})")


    year2 = 2024
    circuit_list_2024 = []
 
    # Loop su tutti i round del campionato (22 round per il 2023)
    for round_number in range(1, 25):  
        try:
            event = fastf1.get_event(year2, round_number)  # Recupera l'evento
            circuit_list_2024.append({
                "Round": round_number,
                "Nome GP": event.EventName,  # Nome del Gran Premio
                "Circuito": event.Location,  # Nome del circuito
                "Data": year2  # Data dell'evento
            })
        except Exception as e:
            print(f"Errore nel caricare il round {round_number}: {e}")

    # # Stampa l'elenco dei circuiti
    # # for circuit in circuit_list_2024:
        
    #     # print(f"Round {circuit['Round']}: {circuit['Nome GP']} - {circuit['Circuito']} ({circuit['Data']})")
    print("cirucits list full: ", circuit_list_2023 + circuit_list_2024)
    collection.insert_many(circuit_list_2023 + circuit_list_2024)  
    # Stop the Spark context
    # sc.stop()
    retrieved_gps = collection.find({},{"Round":1,"Data":1,"Nome GP":1})
    for i in retrieved_gps:
        print("trying to extract data for ",i["Data"], i["Round"],i["Nome GP"])
        get_drivers(i["Data"], i["Round"],i["Nome GP"])



if __name__ == "__main__":
    client = MongoClient("mongodb://mongo_data:27017")
    db = client["f1_data"]
    collection = db["circuits_info"] 
    drivers_collection = db["drivers_info"]
    main()




# from pyspark.sql import SparkSession
# import requests
# from pymongo import MongoClient
# from itertools import product, chain
# import json
# from pyspark.sql.functions import col


# from pyspark.sql import SparkSession

# def get_data():
#     spark = SparkSession.builder \
#         .appName("Spark Setup Test") \
#         .config('spark.ui.port', '4040') \
#         .config("spark.jars.packages", 'org.mongodb.spark:mongo-spark-connector_2.12:10.3.0') \
#         .config("spark.mongodb.connection.uri", "mongodb://mongo_data:27017/f1_data") \
#         .getOrCreate()


#     drivers_data = spark.read.format("mongodb") \
#         .option("database", "f1_data") \
#         .option("collection", "drivers") \
#         .load()

#     data = drivers_data.select(col("driver_number"),col("team_name"),col("full_name"),col("name_acronym")).rdd.collect()
#     print("data = ", data)
#     # Simple RDD operation for testing
#     # data = [1, 2, 3, 4, 5]
#     rdd = spark.sparkContext.parallelize(data)
#     squared = rdd.map(lambda x: x**2).collect()
#     print("Squared Numbers:", squared)

#     spark.stop()

# if __name__ == "__main__":

    
#     get_data()






# # Step 1: Set up the Spark session and MongoDB connector
# spark = SparkSession.builder \
#     .appName("API to MongoDB Multi-Endpoint") \
#      .config('spark.ui.port', '4040') \
#     .config("spark.jars.packages", 'org.mongodb.spark:mongo-spark-connector_2.12:10.3.0') \
#     .config("spark.mongodb.connection.uri", "mongodb://mongo_data:27017/f1_data") \
#     .getOrCreate()

# client = MongoClient("mongodb://mongo_data:27017")

# # Step 2: Define the function to call the API and return data
# def fetch_api_data(api_url):
#     response = requests.get(api_url)
#     if response.status_code == 200:
#         return response.json()  # Assumes API returns JSON data
#     else:
#         return None
    
# def call_endpoints_in_partition(partition):
#     session = requests.Session()  # Create a session for efficient HTTP calls
#     # print("partition: ", partition)
#     for endpoint in partition:
#         # print("endpoint to call: ", endpoint)
#         try:
#             response = session.get(endpoint)
#             print(f"Called {endpoint}, Status Code: {response.status_code}")
#         except Exception as e:
#             print(f"Error calling {endpoint}: {e}")
#     df = spark.createDataFrame(response.json)
#     write_config = {
#         "spark.mongodb.write.connection.uri": "mongodb://mongo_data:27017/f1_data.positions"
#     }
#     df.write.format("mongodb").mode("append").options(**write_config).save()
# ## definisco i diversi parametri da passare ad ogni endpoint 
# ## position richiede: driver number e session key; bisogna ottenre session key per qualifiche e race 
# ## bisogna ottenere session key per qualifica, sprint e race di ogni gran premio  
# ## session type = Qualifying restituisce tutte le sessioni per sessioni di qualifica (normale o shootout)
# ## session type = Race restituisce sia gara normale che sprint race
# ## session key si possono salvare su collection oppure utilizzare direttamente
# circuits_parameters = ["Italy","Spain","Belgium"]
# drivers_parameters  = ["16","55","11","1","14"] ## n_drivers 
# country_names       = ["Italy","Spain","Belgium"]
# years               = ["2023","2024"]
# sessions_to_retrieve = ["Qualifying", "Race"]
# ## info necessarie
# # keys_object = {
# #     "location"      :   "", ## nome circuito
# #     "session_key"   :   "",
# #     "meeting_key"   :   "",
# #     "session_name"  :   "",

# # }
# keys_info = ["location","session_key","meeting_key","session_name","year"]
# keys_object = []
# for country in country_names:
#     for year in years:
#         for session in sessions_to_retrieve:
#             session_endpoint = f"https://api.openf1.org/v1/sessions?country_name={country}&year={year}&session_type={session}"
#             keys_results  = requests.get(session_endpoint).json()
#             filtered_results = [
#                 {field: session[field] for field in keys_info} for session in keys_results] 
#             # print("LENGTH OF EXTRACTED DATA: ", len(filtered_results))
#             keys_object.append(filtered_results)

# # print("EXTRACTED DATA OF DIMENSION: ", len(keys_object))

# # print("filtered data; ", keys_object)

# ## retrieving position data for drivers using session keys 
# # 
# # 1 - filtering session keys for qualyifing and races 
# # 2 - define a grid for efficiently request data through spark 
# # 3 - make the request for each driver
# #  
# ## oggetto da prendere dai dati
# position_obj = {
#     "location" : "",
#     "year"      :"",
#     "session_type" : "",
#     "driver_number"       : "", 
#     "position"            :"",

# }
# keys_object = list(chain.from_iterable(keys_object))
# # print("KEYS OBJECT = ", keys_object)
# postion_requests_params = [
#     {
#         "driver": driver,
#         "meeting_key": param["meeting_key"],
#         "session_key": param["session_key"]
        
#     }
#     for driver, param in product(drivers_parameters, keys_object)
# ]

# # print(postion_requests_params)

# endpoint_calls = [
#     {"endpoint" : f"https://api.openf1.org/v1/position?meeting_key={param['meeting_key']}&gdriver_number={param['driver']}"}
#     for param in postion_requests_params
# ]

# # print("endpoints to call = \n", endpoint_calls)

# # Step 5: Create an RDD with the endpoint, collection, and parameters
# tasks_rdd = spark.sparkContext.parallelize(endpoint_calls, numSlices=len(endpoint_calls))
# print(tasks_rdd)
# # Step 6: Process each partition
# tasks_rdd.foreachPartition(call_endpoints_in_partition) ## call api in partition prende in input una partition (iterator)

# # Stop the Spark session
# # spark.stop()

# # key_requests = [
# #     {"endpoint": "https://your.api/endpoint1", "collection": "drivers", "params": {"season": season, "country": country}}
# #     for season, country in product(seasons, countries)
# # ]
# ## set di parametri da passare creato dinamicamente
# # Define possible values for parameters

# # Generate all combinations of parameters
# # endpoint_collection_params = [
# #     {"endpoint": "https://your.api/endpoint1", "collection": "drivers", "params": {"season": season, "country": country}}
# #     for season, country in product(seasons, countries)
# # ]
# # # Step 4: Define endpoint to collection mapping
# # endpoint_params = [
# #     {"endpoint": "https://your.api/endpoint1","params" : circuits_parameters, "collection_name": "circuits"},
# #     {"endpoint": "https://your.api/endpoint1","params" : drivers_parameters, "collection_name": "drivers"},

# # ]

# # endpoint_collection_map = {
# #     "https://your.api/endpoint1": "drivers",
# #     "https://your.api/endpoint2": "constructors",
# #     "https://your.api/endpoint3": "races",
# # }




# # Step 5: Create an RDD with tasks for each endpoint
# # Each element is a tuple (endpoint, collection)
# # tasks = [(endpoint, collection) for endpoint, collection in endpoint_params.items()]
# # ## parallelize porta la collection (struttura dati attuale) ad un RDD che può essere operato in parallelo
# # tasks_rdd = spark.sparkContext.parallelize(tasks, numSlices=len(tasks))

# # # Step 6: Process each partition
# # def process_partition(partition):
# #     endpoint_params = dict(partition)  # Convert the partition into a dictionary
# #     call_api_in_partition(range(10000), endpoint_params)  # Replace range(10000) with your desired data range

# # tasks_rdd.foreachPartition(process_partition)

# # # Stop the Spark session
# # spark.stop()




# # from pyspark.sql import SparkSession
# # from urllib.request import urlopen
# # import json
# # import findspark
# # findspark.init()

# # spark = SparkSession.builder\
# #         .master("local")\
# #         .appName("MongoExample")\
# #         .config('spark.ui.port', '4040') \
# #         .config("spark.jars.packages", 'org.mongodb.spark:mongo-spark-connector_2.12:10.3.0') \
# #         .config("spark.mongodb.connection.uri", "mongodb://mongo_data:27017/f1_data.drivers") \
# #         .getOrCreate()



# # response = urlopen('https://api.openf1.org/v1/sessions?country_name=Italy&year=2024')
# # data = json.loads(response.read().decode('utf-8'))
# # print("gathering data....", len(data))

# # write_config = {
# #     "spark.mongodb.write.connection.uri": "mongodb://mongo_data:27017/f1_data.drivers"
# # }

# # df = spark.createDataFrame(data)

# # df.write.format("mongodb").mode("append").options(**write_config).save()

# # spark.stop()