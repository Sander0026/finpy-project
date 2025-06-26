from flask import Blueprint, request, flash, redirect, url_for, session, render_template
import mysql.connector
from mysql.connector import Error
from .db import create_db_connection

bp = Blueprint('transactions', __name__)

@bp.route('/adicionar_transacao', methods=['POST'])
def adicionar_transacao():
     
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para adicionar uma transação.', 'warning')
        return redirect(url_for('auth.login'))
     
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    data = request.form.get('data')
    tipo = request.form.get('tipo')
    categoria_id = request.form.get('categoria_id')
    
    
    if not all([descricao, valor, data, tipo]):
        flash('Todos os campos são obrigatórios.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        query_insert = "INSERT INTO transacoes (usuario_id, descricao, valor, data, tipo, categoria_id) VALUES (%s, %s, %s, %s, %s, %s)"
        dados_transacao = (session['usuario_id'], descricao, valor, data, tipo, categoria_id)
        cursor.execute(query_insert, dados_transacao)
        con.commit()
        flash('Transação adicionada com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
    
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('main.dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 
            
@bp.route('/deletar_transacao/<int:transacao_id>', methods=['POST'])  
def deletar_transacao(transacao_id):
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para deletar uma transação.', 'warning')
        return redirect(url_for('auth.login'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        query_delete = "DELETE FROM transacoes WHERE id = %s AND usuario_id = %s"
        cursor.execute(query_delete, (transacao_id, usuario_id))
        con.commit()
        
        flash('Transação deletada com sucesso!', 'success')
        return redirect(url_for('main.dashboard'))
    
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('main.dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()


@bp.route('/editar_transacao/<int:transacao_id>' , methods=['GET'])
def editar_transacao(transacao_id):
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        flash('Você precisa estar logado para editar uma transação.', 'warning')
        return redirect(url_for('auth.login'))
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)

        query = ("SELECT * FROM transacoes WHERE id = %s")
        cursor.execute(query, (transacao_id,))
        transacao = cursor.fetchone()
        
        query_categorias = "SELECT * FROM categorias WHERE usuario_id = %s"
        cursor.execute(query_categorias, (session['usuario_id'],))
        lista_categorias = cursor.fetchall()
        
        categorias_receita = [] 
        categorias_despesa = [] 
        
        for categoria in lista_categorias:
            if categoria['tipo'] == 'receita':
                # 4. Adicione à lista de receitas
                categorias_receita.append(categoria)
                
            elif categoria['tipo'] == 'despesa':
                # 4. Adicione à lista de despesas
                categorias_despesa.append(categoria)
        
        
        if not transacao or transacao['usuario_id'] != session['usuario_id']:
            flash('Transação não encontrada ou você não tem permissão para editar.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return render_template('editar_transacao.html', transacao=transacao, categorias_receita=categorias_receita, categorias_despesa=categorias_despesa)
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('main.dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()    
            

@bp.route('/atualizar_transacao/<int:transacao_id>', methods=['POST'])
def atualizar_transacao(transacao_id):
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('auth.login'))

    # Pega os dados atualizados do formulário
    descricao = request.form.get('descricao')
    valor = request.form.get('valor')
    data = request.form.get('data')
    tipo = request.form.get('tipo')
    categoria_id = request.form.get('categoria_id')

    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()

        # Query SQL de UPDATE
        # A cláusula "AND usuario_id = %s" é uma camada extra de segurança
        query = """UPDATE transacoes 
                   SET descricao = %s, valor = %s, data = %s, tipo = %s , categoria_id = %s
                   WHERE id = %s AND usuario_id = %s"""
        
        params = (descricao, valor, data, tipo, categoria_id, transacao_id, session['usuario_id'])
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

    return redirect(url_for('main.dashboard'))

@bp.route('/lancamentos')
def lancamentos():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver esta página.', 'warning')
        return redirect(url_for('auth.login'))
     
    con = None
    cursor = None
    try:
        # A lógica para buscar as transações 
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)
        
        query = "SELECT * FROM transacoes WHERE usuario_id = %s ORDER BY data DESC"
        cursor.execute(query, (session['usuario_id'],)) 
        lista_transacoes = cursor.fetchall()
        
        query_categorias = "SELECT * FROM categorias WHERE usuario_id = %s"
        cursor.execute(query_categorias, (session['usuario_id'],))
        lista_categorias = cursor.fetchall()
        
        categorias_receita = [] 
        categorias_despesa = [] 
        
        for categoria in lista_categorias:
            if categoria['tipo'] == 'receita':
                # 4. Adicione à lista de receitas
                categorias_receita.append(categoria)
                
            elif categoria['tipo'] == 'despesa':
                # 4. Adicione à lista de despesas
                categorias_despesa.append(categoria)
        
        
        return render_template('lancamentos.html',transacoes=lista_transacoes, categorias_receita=categorias_receita, categorias_despesa=categorias_despesa)
    except Error as e:
        flash(f"Ocorreu um erro no sistema: {e}", 'danger')
        return redirect(url_for('main.dashboard'))
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()