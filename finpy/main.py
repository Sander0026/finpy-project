from flask import Blueprint, render_template, redirect, url_for, session, flash
import mysql
from mysql.connector import Error
from .db import create_db_connection


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Verifica se o usuário já está logado (se a chave 'usuario_id' existe na sessão)
    if 'usuario_id' in session:
        # Se estiver logado, redireciona para o dashboard
        return redirect(url_for('main.dashboard'))
    else:
        # Se não estiver logado, redireciona para a página de login
        return redirect(url_for('auth.login'))


    
@bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))
     
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
        return redirect(url_for('auth.login'))       
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 