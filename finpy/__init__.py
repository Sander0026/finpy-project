from flask import Flask

def create_app():
    # Cria a instância da aplicação
    app = Flask(__name__)
    
    # Configura a chave secreta
    app.config['SECRET_KEY'] = 's@aNd3r*66' # Ou sua chave

    # Importa e registra os blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)

    from . import transactions
    app.register_blueprint(transactions.bp)

    # Torna a rota 'index' do blueprint 'main' a rota principal
    app.add_url_rule('/', endpoint='index')
 
    return app