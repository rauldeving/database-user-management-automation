import os
import yaml
import boto3
import json
import psycopg2
import pymysql
import sys

if len(sys.argv) < 2:
    print("Usage: python manage_users.py <environment>")
    sys.exit(1)

environment = sys.argv[1].lower()
print(f"Running user management for: {environment.upper()}")

# Define secret name in  AWS
db_secret_name = f"db-secrets-{environment}"   
user_secret_name = f"db-users-{environment}"   

aws_region = "eu-central-1"

# Init boto3 for AWS Secrets Manager
client = boto3.client("secretsmanager", region_name=aws_region)

def get_secret(secret_name):
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

try:
    db_secrets = get_secret(db_secret_name)   # Secret for db details such as db host, username & password
    user_secrets = get_secret(user_secret_name)  # Secret for passwords
except Exception as e:
    print(f"Error retrieving secrets from AWS: {e}")
    sys.exit(1)

# Read users.yaml
try:
    with open("users.yaml", "r") as f:
        users = yaml.safe_load(f)
except Exception as e:
    print(f"Error reading users.yaml: {e}")
    sys.exit(1)

for db in db_secrets["databases"]:
    db_host = db["host"]
    db_username = db["username"]
    db_password = db["password"]
    db_name = db.get("database", "postgres")  # If DB not defined, it will use postgres - the only one supported up to this point

    print(f"Connecting to PostgreSQL database: {db_host}...")

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(host=db_host, user=db_username, password=db_password, dbname=db_name)
        cursor = conn.cursor()

        for user in users["users"]:
            user_name = user["name"]
            user_password = user_secrets.get(user_name)

            if user_password:
                print(f"Creating PostgreSQL user: {user_name} on {db_host}")

                # Create user and grant connect permission
                cursor.execute(f"CREATE USER {user_name} WITH PASSWORD '{user_password}';")
                cursor.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {user_name};")

                # Grant roles 
                if environment == "production":
                    cursor.execute(f"GRANT pg_read_all_data TO {user_name};")
                    print(f"Granted pg_read_all_data to {user_name} on {db_host}")
                else:
                    cursor.execute(f"GRANT rds_superuser TO {user_name};")
                    print(f"Granted rds_superuser to {user_name} on {db_host}")

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error with PostgreSQL database {db_host}: {e}")

print("User creation completed successfully!")
