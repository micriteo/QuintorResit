import psycopg2
from pymongo import MongoClient
from flask import Flask


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo. Use your own connection string
    # CONNECTION_STRING = "mongodb+srv://IT2C:ZHty3DkM0tIozYks@it2csportsaccounting.byzfgpv.mongodb.net/?retryWrites=true&w=majority"
    CONNECTION_STRING = "mongodb+srv://admin:55TPmsPXgRraJuvE@cluster0.lxrxapc.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['IT2CSportsAccounting']


def get_collection():
    namedb = get_database()
    transactions_collection = namedb["Transactions"]
    return transactions_collection


# def get_flask_app():
#     app = Flask(__name__)
#     return app


def get_connection_postgre():
    # Establishing the connection
    conn = psycopg2.connect(
        user="admingamer", password="Lololol1",
        host="quintorsportsresit.postgres.database.azure.com", port=5432, database="postgres"
    )
    print(conn)
    return conn


def get_connection_postgre_user():
    # Establishing the connection
    # conn = psycopg2.connect(
    #     database="postgres", user='myuser', password='user', host='localhost', port='5432'
    # )
    # return conn
    return None



# This is added so that many files can reuse the function get_database()
# if __name__ == "__main__":
#     # Get the database
#     dbname = get_database()
