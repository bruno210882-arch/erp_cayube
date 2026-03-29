from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ================= DATABASE =================
uri = os.getenv("DATABASE_URL")

if not uri:
    raise RuntimeError("DATABASE_URL não configurado!")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    local = db.Column(db.String(100))
    divida = db.Column(db.Float, default=0)
    telefone = db.Column(db.String(20))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    preco = db.Column(db.Float)
    custo = db.Column(db.Float)
    estoque = db.Column(db.Integer)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer)
    cliente_id = db.Column(db.Integer)
    quantidade = db.Column(db.Integer)
    total = db.Column(db.Float)
    pago = db.Column(db.Boolean)

class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dinheiro = db.Column(db.Float, default=0)
    conta = db.Column(db.Float, default=0)

# ================= INIT =================
with app.app_context():
    db.create_all()

def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo

# ================= ROTAS =================

@app.route('/')
def index():
    saldo = get_saldo()
    return render_template('index.html', saldo=saldo)

@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/venda')
def venda():
    return render_template('venda.html')

@app.route('/fiado')
def fiado():
    return render_template('fiado.html')

@app.route('/movimentacao')
def movimentacao():
    return render_template('movimentacao.html')

@app.route('/entrada_estoque')
def entrada_estoque():
    return render_template('entrada_estoque.html')

@app.route('/relatorio_financeiro')
def relatorio_financeiro():
    return render_template('relatorio_financeiro.html')

@app.route('/relatorio_estoque')
def relatorio_estoque():
    return render_template('relatorio_estoque.html')

@app.route('/relatorio_lucro')
def relatorio_lucro():
    return render_template('relatorio_lucro.html')

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)