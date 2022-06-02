import sqlite3
from typing import Union

from schemas.user import User

def get_connection():
    return sqlite3.connect('/tmp/users.db')

def generate_fake_users():
    con = get_connection()
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users
               (id text, username text, password text, role text)''')
    cur.execute("DELETE FROM users")
    cur.execute("INSERT INTO users VALUES ('49cbf85b-6354-447c-b23d-d01f521696a3', 'alice', 'strongP@s$w0rd', 'player'), ('076ce020-23c9-4795-8243-632191b6f9e0','bob','otherstrongP@s$w0rd', 'player'), ('0083932a-07bd-42c8-a0ec-5579435f3627', 'charlie', 'root', 'admin')")
    con.commit()
    con.close()

def get_user(username: str, password: str) -> Union[User, None]:
    user = None

    con = get_connection()
    cur = con.cursor()

    if len((result := cur.execute('SELECT id, role FROM users WHERE username=:username AND password=:password', {"username": username, "password": password}).fetchall())) > 0:
        for unique_row in result:
            user = User(id=unique_row[0], username=username, role=unique_row[1])
    return user