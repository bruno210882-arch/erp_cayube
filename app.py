from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import os

app = Flask(__name__)


# ================== BANCO ==================

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


db = SQLAlchemy(app)

# ================== MODELS (exemplo) ==================
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)

class Fiado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    quantidade = db.Column(db.Integer)

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

# ================= FUNÇÃO SALDO =================

def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo

# ================= DASHBOARD =================


# ================== DASHBOARD ==================
@app.route('/')
def index():

    total_vendas = db.session.query(func.sum(Venda.valor)).scalar() or 0
    total_despesas = db.session.query(func.sum(Despesa.valor)).scalar() or 0
    total_fiado = db.session.query(func.sum(Fiado.valor)).scalar() or 0
    total_estoque = db.session.query(func.sum(Produto.quantidade)).scalar() or 0

    lucro_total = total_vendas - total_despesas

    saldo = get_saldo()

    vendas = Venda.query.all()
    produtos = Produto.query.all()

    # Simulação de caixa (ajuste se tiver campo real)
    saldo = {
        "dinheiro": total_vendas * 0.4,
        "conta": total_vendas * 0.6
    }

    return render_template(
        'index.html',
        saldo=saldo,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro_total
    )


# ================== START ==================

# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)