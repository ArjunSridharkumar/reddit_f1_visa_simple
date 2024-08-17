import psycopg2
from psycopg2 import sql
from read_parameters import load_parameters

try:
    parameters = load_parameters("list_of_parameters.txt")
except Exception as e:
    raise(e)
    import pdb;pdb.set_trace()
EMBEDDING_MODEL_NAME = parameters['EMBEDDING_MODEL_NAME']
EMBEDDING_MAX_TOKENS = int(parameters['EMBEDDING_MAX_TOKENS'])
PROMPT_ENGG_METHOD = parameters['PROMPT_ENGG_METHOD']
VECTOR_STORE_METHOD = parameters['VECTOR_STORE_METHOD']
VECTOR_INDEX_METHOD = parameters['VECTOR_INDEX_METHOD']
LLM_MODEL_NAME = parameters['LLM_MODEL_NAME']
POSTGRES_DB_NAME=parameters['POSTGRES_DB_NAME']
POSTGRES_DB_USER=parameters['POSTGRES_DB_USER']
POSTGRES_DB_PASSWORD=parameters['POSTGRES_DB_PASSWORD']
POSTGRES_DB_HOST=parameters['POSTGRES_DB_HOST']
POSTGRES_DB_PORT=parameters['POSTGRES_DB_PORT']



conn = psycopg2.connect(
    dbname="postgres",
    user="arjunsridharkumar",
    password="Convocation@2024",
    host=POSTGRES_DB_HOST,
    port=POSTGRES_DB_PORT
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE DATABASE reddit_db_1;")

cur.close()
conn.close()

#Creating the reddit database
conn = psycopg2.connect(
    dbname=POSTGRES_DB_NAME,
    user=POSTGRES_DB_USER,
    password=POSTGRES_DB_PASSWORD,
    host=POSTGRES_DB_HOST,
    port=POSTGRES_DB_PORT
)
cur = conn.cursor()

#Install the extension pgvector, else vector will be a unknown type for postgresql
cur.execute('''CREATE EXTENSION IF NOT EXISTS vector;''')

#Creating the posts table
cur.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title_content TEXT,
        embedding vector(1536)
    );
''')


#Creating a comments table. Will reference the posts table's id as foreign key.
cur.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        post_id INTEGER REFERENCES posts(id),
        content TEXT,
        embedding vector(1536)
    );
''')

conn.commit()
cur.close()
conn.close()

print("Database and tables created successfully.")