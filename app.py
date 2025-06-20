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
    senha_login = request.form.get('senha')
    email_login = request.form.get('email')
    
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
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver esta página.', 'warning')
        return redirect(url_for('login'))
     
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)
        query_usuarios = "SELECT * FROM transacoes WHERE usuario_id = %s ORDER BY data DESC"
        cursor.execute(query_usuarios, (session['usuario_id'],)) 
        
        lista_transacoes = cursor.fetchall()
        
        query_total_receitas = "SELECT SUM(valor) AS total FROM transacoes WHERE tipo = 'receita' AND usuario_id = %s"
        cursor.execute(query_total_receitas, (session['usuario_id'],))
        total_receitas = cursor.fetchone()
        
        query_total_despesas = "SELECT SUM(valor) AS total FROM transacoes WHERE tipo = 'despesa' AND usuario_id = %s"
        cursor.execute(query_total_despesas, (session['usuario_id'],))
        total_despesas = cursor.fetchone()
        
        total_despesa = total_despesas['total'] if total_despesas['total'] else 0
        total_receita = total_receitas['total'] if total_receitas['total'] else 0
        
        saldo = total_receita - total_despesa
        
        
        
        
        if not lista_transacoes:
            flash('Nenhuma transação encontrada. Adicione uma transação para começar.', 'info')
            return render_template('dashboard.html', transacoes=[])
        else:
            return render_template('dashboard.html', 
                       transacoes=lista_transacoes,
                       receitas=total_receita,
                       despesas=total_despesa,
                       saldo=saldo)
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('login'))       
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()   
    
@app.route('/adicionar_transacao', methods=['POST'])
def adicionar_transacao():
    
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para adicionar uma transação.', 'warning')
        return redirect(url_for('login'))
    
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    data = request.form.get('data')
    tipo = request.form.get('tipo')
    
    
    if not all([descricao, valor, data, tipo]):
        flash('Todos os campos são obrigatórios.', 'danger')
        return redirect(url_for('dashboard'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        query_insert = "INSERT INTO transacoes (usuario_id, descricao, valor, data, tipo) VALUES (%s, %s, %s, %s, %s)"
        dados_transacao = (session['usuario_id'], descricao, valor, data, tipo)
        cursor.execute(query_insert, dados_transacao)
        con.commit()
        flash('Transação adicionada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 
            
@app.route('/deletar_transacao/<int:transacao_id>', methods=['POST'])  
def deletar_transacao(transacao_id):
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para deletar uma transação.', 'warning')
        return redirect(url_for('login'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        query_delete = "DELETE FROM transacoes WHERE id = %s AND usuario_id = %s"
        cursor.execute(query_delete, (transacao_id, usuario_id))
        con.commit()
        
        flash('Transação deletada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()


@app.route('/editar_transacao/<int:transacao_id>' , methods=['GET'])
def editar_transacao(transacao_id):
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para editar uma transação.', 'warning')
        return redirect(url_for('login'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)

        query = ("SELECT * FROM transacoes WHERE id = %s")
        cursor.execute(query, (transacao_id,))
        transacao = cursor.fetchone()
        
        if not transacao or transacao['usuario_id'] != session['usuario_id']:
            flash('Transação não encontrada ou você não tem permissão para editar.', 'danger')
            return redirect(url_for('dashboard'))
        
        return render_template('editar_transacao.html', transacao=transacao)
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()    
            

@app.route('/atualizar_transacao/<int:transacao_id>', methods=['POST'])
def atualizar_transacao(transacao_id):
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))

    # Pega os dados atualizados do formulário
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    data = request.form.get('data')
    tipo = request.form.get('tipo')

    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        # Query SQL de UPDATE
        # A cláusula "AND usuario_id = %s" é uma camada extra de segurança
        query = """UPDATE transacoes 
                   SET descricao = %s, valor = %s, data = %s, tipo = %s 
                   WHERE id = %s AND usuario_id = %s"""
        
        params = (descricao, valor, data, tipo, transacao_id, session['usuario_id'])
        cursor.execute(query, params)
        con.commit()

        flash('Transação atualizada com sucesso!', 'success')

    except Error as e:
        flash(f"Erro ao atualizar a transação: {e}", "danger")
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)