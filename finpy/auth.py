from mysql.connector import Error
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import create_db_connection
import mysql.connector

# Cria o Blueprint.
# 'auth' é o nome do blueprint.
# url_prefix='/auth' significa que todas as rotas deste arquivo começarão com /auth (ex: /auth/login)
bp = Blueprint('auth', __name__, url_prefix='/auth')

 
@bp.route('/cadastro', methods=['GET'])
def cadastro():
    return render_template('cadastro.html')


@bp.route('/registrar', methods=['POST'])
def registrar_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
        
    if senha != confirmar_senha:
        flash('As senhas não coincidem. Por favor, tente novamente.', 'danger') 
        return redirect(url_for('auth.cadastro'))   
    
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
            return redirect(url_for('auth.cadastro'))
        else:   
             
            hash_senha = generate_password_hash(senha)
            
            query_insert = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
            dados_usuario = (nome, email, hash_senha)
            
            cursor.execute(query_insert, dados_usuario)
            con.commit()
            
            flash('Cadastro realizado com sucesso! Faça seu login.', 'success')
            return redirect(url_for('auth.login'))
             
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')  
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()  
    
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@bp.route('/autenticar' , methods=['POST'])
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
            return redirect(url_for('main.dashboard'))
        else:
            flash('Senha incorreta. Por favor, tente novamente.', 'danger')
            return redirect(url_for('auth.login'))
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('auth.login'))

    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 

@bp.route('/logout')
def logout():
    session.clear()  # Limpa a sessão do usuário
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('auth.login'))
