import sqlite3
for col in [desc[0] for desc in sqlite3.connect('app.db').execute('SELECT * FROM plane_data LIMIT 1').description]:
    print(col)
