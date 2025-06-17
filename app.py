from flask import Flask

# Cria uma instância da aplicação Flask
app = Flask(__name__)

# Define a rota principal da aplicação
@app.route('/')
def home():
    return "Olá, FinPy! Meu servidor está no ar."

# Permite que o servidor seja executado quando o script é chamado diretamente
if __name__ == '__main__':
    app.run(debug=True)