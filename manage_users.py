import os
import yaml
import boto3
import json
import psycopg2
import sys

if len(sys.argv) < 2:
    print("Usage: python manage_users.py <environment>")
    sys.exit(1)

environment = sys.argv[1].lower()
print(f"Running user management for: {environment.upper()}")

# ARN-urile secretelor sunt definite în Task Definition (ca environment variables)
db_secret_arn = os.getenv("DB_SECRET_ARN")
user_secret_arn = os.getenv("USER_SECRET_ARN")

if not db_secret_arn or not user_secret_arn:
    print("Error: Missing secret ARNs in environment variables")
    sys.exit(1)

aws_region = "eu-central-1"

# Init boto3 pentru AWS Secrets Manager
client = boto3.client("secretsmanager", region_name=aws_region)

def get_secret(secret_arn):
    """ Extrage un secret din AWS Secrets Manager și îl parsează ca JSON """
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])

try:
    db_secrets = get_secret(db_secret_arn)   # Secret cu detalii despre baze de date
    user_secrets = get_secret(user_secret_arn)  # Secret cu parolele userilor
except Exception as e:
    print(f"Error retrieving secrets from AWS: {e}")
    sys.exit(1)

# Citim fișierul users.yaml
try:
    with open("users.yaml", "r") as f:
        users = yaml.safe_load(f)
except Exception as e:
    print(f"Error reading users.yaml: {e}")
    sys.exit(1)

# Funcție pentru a verifica dacă un user există deja în baza de date
def user_exists(cursor, user_name):
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (user_name,))
    return cursor.fetchone() is not None

# Iterăm prin fiecare bază de date
for db in db_secrets["databases"]:
    db_host = db["host"]
    db_username = db["username"]
    db_password = db["password"]
    db_name = db.get("database", "postgres")

    print(f"Connecting to PostgreSQL database: {db_host}...")

    try:
        conn = psycopg2.connect(host=db_host, user=db_username, password=db_password, dbname=db_name)
        cursor = conn.cursor()

        for user in users["users"]:
            user_name = user["name"]
            user_password = user_secrets.get(user_name)

            if not user_password:
                print(f"Skipping {user_name}: No password found in AWS Secrets Manager")
                continue

            if user_exists(cursor, user_name):
                print(f"User {user_name} already exists in {db_host}, skipping...")
                continue

            print(f"Creating PostgreSQL user: {user_name} on {db_host}")

            # Creăm user-ul și îi oferim acces la conectare
            cursor.execute(f"CREATE USER {user_name} WITH PASSWORD '{user_password}';")
            cursor.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {user_name};")

            # Atribuim rolurile corespunzătoare în funcție de environment
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
