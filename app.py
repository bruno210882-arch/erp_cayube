from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)

# ================== BANCO ==================
uri = os.getenv("DATABASE_URL")

if not uri:
    raise RuntimeError("DATABASE_URL não configurado!")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# ================== DASHBOARD ==================
@app.route('/')
def index():

    total_vendas = db.session.query(func.sum(Venda.valor)).scalar() or 0
    total_despesas = db.session.query(func.sum(Despesa.valor)).scalar() or 0
    total_fiado = db.session.query(func.sum(Fiado.valor)).scalar() or 0
    total_estoque = db.session.query(func.sum(Produto.quantidade)).scalar() or 0

    lucro_total = total_vendas - total_despesas

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
if __name__ == '__main__':
    app.run(debug=True)