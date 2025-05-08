import os
from dotenv import load_dotenv
import mysql.connector.pooling

load_dotenv()  

config={
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "host":os.getenv("DB_HOST"),
    "database":os.getenv("DB_NAME")
    }

cnxpool=mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=20, **config)


