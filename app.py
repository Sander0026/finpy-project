from flask import Flask
import mysql.connector
from mysql.connector import Error
from flask import flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 's@aNd3r*66'  # Chave secreta para sessões e mensagens flash

@app.route('/')
def index():
    # Verifica se o usuário já está logado (se a chave 'usuario_id' existe na sessão)
    if 'usuario_id' in session:
        # Se estiver logado, redireciona para o dashboard
        return redirect(url_for('dashboard'))
    else:
        # Se não estiver logado, redireciona para a página de login
        return redirect(url_for('login'))

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

@app.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
        
    if senha != confirmar_senha:
        flash('As senhas não coincidem. Por favor, tente novamente.', 'danger') 
        return redirect(url_for('cadastro'))   
    
    con = None
    cursor = None
    try:
        con =  create_db_connection()
        cursor = con.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios WHERE email = %s" 
        cursor.execute(query, (email,)) 
        
        email_existente = cursor.fetchone() 
        
        if email_existente:
            flash('Este email já está cadastrado. Tente outro.', 'danger')
            return redirect(url_for('cadastro'))
        else:   
            
            hash_senha = generate_password_hash(senha)
            
            query_insert = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
            dados_usuario = (nome, email, hash_senha)
            
            cursor.execute(query_insert, dados_usuario)
            con.commit()
            
            flash('Cadastro realizado com sucesso! Faça seu login.', 'success')
            return redirect(url_for('login'))
             
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')  
    
    finally:
    # Passo Bônus: Fechar tudo
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()  
    
    return redirect(url_for('login'))
    

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/autenticar' , methods=['POST'])
def autenticar():
    senha_login = request.form.get('senha_usuario')
    email_login = request.form.get('email_usuario')
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(query, (email_login,))
        
        usuario_do_banco = cursor.fetchone()
        
        if usuario_do_banco and check_password_hash(usuario_do_banco['senha'], senha_login):
            flash('Login realizado com sucesso!', 'success')
            session['usuario_id'] = usuario_do_banco['id']
            session['usuario_nome'] = usuario_do_banco['nome']
            return redirect(url_for('dashboard'))
        else:
            flash('Senha incorreta. Por favor, tente novamente.', 'danger')
            return redirect(url_for('login'))
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('login'))

    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()    
    

@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão do usuário
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Futuramente, esta página mostrará as finanças do usuário
    # Por enquanto, vamos apenas garantir que ela exista
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver esta página.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)

