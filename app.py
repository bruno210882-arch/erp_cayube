from flask import Flask, render_template, request, redirect, url_for
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

class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))
    valor = db.Column(db.Float)
    origem = db.Column(db.String(20))
    descricao = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.utcnow)

class MovimentoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer)
    tipo = db.Column(db.String(20))
    quantidade = db.Column(db.Integer)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)

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

    vendas = Venda.query.all()
    produtos = Produto.query.all()

    total_vendas = sum(v.total for v in vendas if v.pago)
    total_fiado = sum(v.total for v in vendas if not v.pago)
    total_estoque = sum(p.estoque for p in produtos)

    lucro_total = 0
    for v in vendas:
        produto = Produto.query.get(v.produto_id)
        if produto:
            custo = produto.custo or 0
            lucro_total += (v.total - (custo * v.quantidade))

    return render_template('index.html',
        saldo=saldo,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro_total
    )

@app.route('/initdb')
def initdb():
    db.create_all()
    return "Banco criado!"
# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)