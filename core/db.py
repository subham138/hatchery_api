import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_config = {
    "host": os.getenv('MYSQL_HOST'),
    "database": os.getenv('MYSQL_DB'),
    "user": os.getenv('MYSQL_USER'),
    "password": os.getenv('MYSQL_PASSWORD'),
}

# Connect to MySQL
def connect():
    # db = mysql.connector.pooling.MySQLConnectionPool(pool_name="timesheet", pool_size=5, pool_reset_session=True, **db_config)
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )
    # return db