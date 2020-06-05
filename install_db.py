import json, sqlite3
import config

db = sqlite3.connect(config.config['db_name'])

db.execute('''DROP TABLE IF EXISTS users''') # Old case

db.execute('''DROP TABLE IF EXISTS tokens''')
db.execute('''CREATE TABLE tokens (id INTEGER PRIMARY KEY, api_token VARCHAR(20) UNIQUE, company INTEGER)''')
db.execute('''INSERT INTO tokens VALUES (null, 'vfuzd2nvaweojqolm4kq', 1) ''')
db.execute('''INSERT INTO tokens VALUES (null, 'ek9chlb4t96sncbr9dgx', 1) ''')
db.execute('''INSERT INTO tokens VALUES (null, 'x6oici7wh3prgx34fxo1', 2) ''')
db.execute('''INSERT INTO tokens VALUES (null, '7eojwd75kqd80m4sm169', 2) ''')
db.execute('''INSERT INTO tokens VALUES (null, 'jyrvm14k9tvdiesxwgku', 3) ''')

db.execute('''DROP TABLE IF EXISTS companies''')
db.execute('''CREATE TABLE companies (id INTEGER PRIMARY KEY, name VARCHAR(50))''')
db.execute('''INSERT INTO companies VALUES (1, 'MegaBank Inc.')''')
db.execute('''INSERT INTO companies VALUES (2, 'Sketchy Steve''s InvestCorp')''')
db.execute('''INSERT INTO companies VALUES (3, 'Nota Bank')''')

db.execute('''DROP TABLE IF EXISTS customers''')
db.execute('''CREATE TABLE customers (id INTEGER PRIMARY KEY, company INTEGER, balance DECIMAL, name TEXT)''')
db.execute('''INSERT INTO customers VALUES (null, 3, 100.00, "Susan")''')
db.execute('''INSERT INTO customers VALUES (null, 1, 1024.63, "Robert")''')
db.execute('''INSERT INTO customers VALUES (null, 1, 651.20, "Juan")''')
db.execute('''INSERT INTO customers VALUES (null, 2, 23651.20, "Arjun")''')
db.execute('''INSERT INTO customers VALUES (null, 1, 12345.49, "Ataahua")''')

db.execute('''DROP TABLE IF EXISTS transfers''')
db.execute("CREATE TABLE transfers (id INTEGER PRIMARY KEY, custID_from INTEGER, custID_to INTEGER, amount DECIMAL, status VARCHAR(10) CHECK(status in ('CREATED', 'PENDING', 'COMPLETE'))) ")
# This table intentionally left blank

db.commit() # NEED this line or changes aren't made
db.close()