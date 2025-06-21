import mysql
from mysql.connector import Error

# Função para criar a conexão com o banco de dados
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # Ou o IP do seu servidor de BD
            user='root',            # Seu usuário do MySQL
            password='Root123456*',    # Sua senha do MySQL
            database='finpy_db'
        ) 
        return connection
    except Error as e:
        print(f"O erro '{e}' ocorreu")
        return None