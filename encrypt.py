import pymysql
from utils import cryption

host = "localhost"
user = "bot"
password = "bot"
database = "bb600"
connection = None
key = b"Tw6G3Lgqs1WJ5aVT7W9doFdUdrmWHvT5WQobQqRisF0="
aes = cryption.FernetEncryption(key)
connection = pymysql.connect(host=host, user=user, password=password, database=database, charset='utf8', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
cursor = connection.cursor()
cursor.execute("SELECT * FROM loggedmessage;")
rows = cursor.fetchall()
for x in rows:
    messageid = x['messageid']
    content = aes.encrypt(x['content']).decode()
    sql = f"UPDATE loggedmessage SET content='{content}' WHERE messageid={messageid};"
    print(sql)
    cursor.execute(sql)
