from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ================= DATABASE =================
uri = os.getenv("DATABASE_URL")
print("DEBUG DATABASE_URL:", uri)

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
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    quantidade = db.Column(db.Integer)
    total = db.Column(db.Float)
    pago = db.Column(db.Boolean)
    forma_pagamento = db.Column(db.String(20))

class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dinheiro = db.Column(db.Float, default=0)
    conta = db.Column(db.Float, default=0)

# ================= INIT DB =================
with app.app_context():
    db.create_all()

# ================= FUNÇÕES =================

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

# ✅ ROTA CLIENTES (CORREÇÃO DO ERRO)
@app.route('/clientes')
def clientes():
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

# ✅ ROTA PRODUTOS
@app.route('/produtos')
def produtos():
    lista = Produto.query.all()
    return render_template('produtos.html', produtos=lista)

# ✅ ROTA VENDAS
@app.route('/vendas')
def vendas():
    lista = Venda.query.all()
    return render_template('vendas.html', vendas=lista)

# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)