import psycopg2
from dependencies import password

conn = psycopg2.connect(database='movies_500', user='postgres', password=password, host='localhost', port='5432')
cursor = conn.cursor()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS movies (
#     id SMALLSERIAL PRIMARY KEY NOT NULL, title VARCHAR(200) NOT NULL, original_title VARCHAR(200),
#      year SMALLINT, description VARCHAR(800))
# """)
# cursor.execute(
#     '''CREATE TABLE users (id SMALLSERIAL PRIMARY KEY NOT NULL, email VARCHAR(100) NOT NULL,
#      username VARCHAR(50) NOT NULL, password VARCHAR(100) NOT NULL)''')

# cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", ('example@example.com', 'user1', 'password123'))
#
cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", ('renmerry@renmerry.com', 'big_love', 'renmerry123'))

cursor.execute('SELECT * FROM movies LIMIT 10')



for row in cursor.fetchall():
    print(row)

# cursor.execute('''DELETE FROM users WHERE id BETWEEN 3 AND 6''')

conn.commit()
cursor.close()
conn.close()