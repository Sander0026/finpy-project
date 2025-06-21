from flask import Blueprint, render_template, session, redirect, url_for, flash

bp = Blueprint('categories', __name__, url_prefix='/categorias')

@bp.route('/')
def index():
    if 'usuario_id' not in session:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('categorias.html')