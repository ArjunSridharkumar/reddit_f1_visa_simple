import psycopg2


conn = psycopg2.connect(
    dbname="reddit_db_1",
    user="codespace",
    password="your_new_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("TRUNCATE TABLE comments, posts ;")
# cur.execute("TRUNCATE TABLE comments;")


conn.commit()
cur.close()
conn.close()