import psycopg2


try:
    print('try')
    # conn = psycopg2.connect(host='localhost', database='wiki', user='postgres', password='postgres')
    conn = psycopg2.connect(host='127.0.0.1', database='wiki', user='postgres', password='1qa2ws3ed', port='5432')
    print("ok")
except Exception as error:
    print('NOT')
    print(error)
    exit(0)

if conn is not None:
    print('Connection established to Postgres')

    # cur = conn.cursor()
    # cur.execute('SELECT * FROM quote;')
    #
    # get_all_data = cur.fetchall()
    # 
    # print(get_all_data)

    conn.close()
else:
    print('Connection not established to Postgres')

print('the end')
