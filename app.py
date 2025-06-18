from flask import Flask
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Função para criar a conexão com o banco de dados
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # Ou o IP do seu servidor de BD
            user='root',            # Seu usuário do MySQL
            password='Root123456*',    # Sua senha do MySQL
            database='finpy_db'
        )
        print("Conexão com o MySQL bem-sucedida")
        return connection
    except Error as e:
        print(f"O erro '{e}' ocorreu")
        return None

@app.route('/')
def home():
    conn = create_db_connection()
    if conn is not None:
        # Se a conexão foi bem-sucedida, podemos fechá-la e retornar uma mensagem
        conn.close()
        return "Conexão com o banco de dados estabelecida com sucesso!"
    else:
        # Se a conexão falhou, retornamos uma mensagem de erro
        return "Falha ao conectar ao banco de dados."

if __name__ == '__main__':
    app.run(debug=True)