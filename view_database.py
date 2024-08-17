import psycopg2


conn = psycopg2.connect(
    dbname="reddit_db_1",
    user="codespace",
    password="your_new_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'posts';")
posts_columns = cur.fetchall()
print(posts_columns)  # Optional: Print the selected rows

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'comments';")
comments_column = cur.fetchall()
print(comments_column)

cur.execute("SELECT * FROM posts LIMIT 10;")
posts = cur.fetchall()
# print(posts)


cur.execute("SELECT * FROM comments LIMIT 10;")
comments = cur.fetchall()
# print(comments)


conn.commit()
cur.close()
conn.close()