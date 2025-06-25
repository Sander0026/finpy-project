from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from finpy.db import create_db_connection

bp = Blueprint('categories', __name__, url_prefix='/categorias')

@bp.route('/')
def index():
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('auth.login'))

    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor(dictionary=True)
        
        query = "SELECT * FROM categorias WHERE usuario_id = %s"
        cursor.execute(query, (session['usuario_id'],))
        
        lista_categorias = cursor.fetchall()
        
        if not lista_categorias:
            flash('Nenhuma categoria encontrada.', 'info')
            return render_template('categorias.html', categorias=[])
    
        return render_template('categorias.html', categorias=lista_categorias)
       
    except Exception as e:
        flash(f'Erro ao acessar categorias: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))
    finally:
        if con:
            con.close()
            
@bp.route('/add', methods=['POST'])
def add():
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('auth.login'))

    nome_categoria = request.form.get('nome_categoria')
    tipo_categoria = request.form.get('tipo_categoria')
    
    if not nome_categoria:
        flash('O nome da categoria é obrigatório.', 'warning')
        return redirect(url_for('categories.index'))
    
    
    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()
        
        query = "INSERT INTO categorias (nome, tipo, usuario_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (nome_categoria, tipo_categoria, session['usuario_id']))
        
        con.commit()
        
        flash('Categoria adicionada com sucesso!', 'success')
        return redirect(url_for('categories.index'))
    
    except Exception as e:
        flash(f'Erro ao adicionar categoria: {str(e)}', 'danger')
        return redirect(url_for('categories.index'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 
            
@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('auth.login'))

    con = None
    cursor = None
    try:
        con = create_db_connection()
        cursor = con.cursor()
        
        query = "DELETE FROM categorias WHERE id = %s AND usuario_id = %s"
        cursor.execute(query, (id, session['usuario_id']))
        
        con.commit()
        
        flash('Categoria excluída com sucesso!', 'success')
        return redirect(url_for('categories.index'))
    
    except Exception as e:
        flash(f'Erro ao excluir categoria: {str(e)}', 'danger')
        return redirect(url_for('categories.index'))
    
    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close() 