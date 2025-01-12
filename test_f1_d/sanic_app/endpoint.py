# from sanic import Sanic
# from sanic.response import json as sanic_json
# from sanic.request import Request
# from sanic.response import HTTPResponse
# import motor.motor_asyncio
from sanic import Sanic, response
from motor.motor_asyncio import AsyncIOMotorClient
import json
from datetime import datetime
import logging
from bson import ObjectId
import logging

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("grafana_api")



app = Sanic("grafana_api")

# Set up MongoDB connection
client = AsyncIOMotorClient("mongodb://mongo_data:27017")  # 'mongo' should match your Docker service name
db = client["f1_data"]
collection = db["drivers"]
car_data = db["car_data"]
drivers_info = db["drivers_info"]


def convert_object_id(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, dict):
            convert_object_id(value)  # Recursively convert for nested documents
    return doc

# @app.route("/data", methods=["POST"])  # or GET if preferred by Grafana
# async def fetch_data(request):
#     logger.info(f"obtained this request: {request}")

#     try:
#         # Define the number of rows to retrieve (you can adjust this limit)
#         limit = 10
#         # limit = request.json.get("limit", 10)  # Fetch 10 rows by default
#         # Query MongoDB
#         cursor = collection.find({}).limit(limit)
#         data = await cursor.to_list(length=limit)

#         # Convert each document's _id to a string for JSON serialization
#         result = [{**row, "_id": str(row["_id"])} for row in data]
        
#         return response.json(result)
#     except Exception as e:
#         # Handle any errors
#         return response.json({"error": str(e)}, status=500)



@app.route("/get_points", methods=["POST"])  # or GET if preferred by Grafana
async def fetch_data(request):
    try:
        cursor = drivers_info.find({})
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "TeamName": "$TeamName",
                        "year": "$Year",
                        "Abbreviation":"$Abbreviation"
                    },  # Group by session_key

                    "team_points": {"$sum": "$Points"}  
                }
            },
            {
                "$project": {
                    "Abbreviation": "$_id.Abbreviation",
                    "team points" : "$team_points",
                    "team name"   : "$_id.TeamName",
                    "year"        : "$_id.year",
                    "_id": 0,  # Exclude the e ntire _id field
                }
            }
        ]

        # Execute the aggregation query
        result = drivers_info.aggregate(pipeline)

        data = await result.to_list()

        # Convert each document's _id to a string for JSON serialization
        result = [{**row, "Abbreviation": str(row["Abbreviation"])} for row in data]
        
        return response.json(result)
    except Exception as e:
        # Handle any errors
        return response.json({"error": str(e)}, status=500)




# @app.route("/get_speed", methods=["POST"])  # or GET if preferred by Grafana
# async def fetch_data(request):
#     logger.info(f"obtained this request: {request}")

#     try:
#         cursor = car_data.find({})
#         pipeline = [
#             {
#                 "$group": {
#                     "_id": "$session_key",  # Group by session_key
#                     "average_speed": {"$avg": "$speed"}  # Calculate average speed
#                 }
#             },
#             {
#                 "$sort": {"_id": 1}  # Optional: Sort results by session_key
#             }
#         ]

#         # Execute the aggregation query
#         result = car_data.aggregate(pipeline)

#         data = await result.to_list()

#         # Convert each document's _id to a string for JSON serialization
#         result = [{**row, "_id": str(row["_id"])} for row in data]
        
#         return response.json(result)
#     except Exception as e:
#         # Handle any errors
#         return response.json({"error": str(e)}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)




## health check ping    
@app.get("/health")
async def health_check(request):
    return response.json({"status": "healthy"})

# Run app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)


