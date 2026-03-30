from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ================= DATABASE =================
uri = os.getenv("DATABASE_URL")
if not uri:
    raise RuntimeError("DATABASE_URL não configurado no Render!")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"))
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"))
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


# ================= DASHBOARD =================
@app.route("/")
def index():
    saldo = get_saldo()

    vendas = Venda.query.all()
    produtos = Produto.query.all()

    total_vendas = sum(v.total for v in vendas if v.pago)
    total_fiado = sum(v.total for v in vendas if not v.pago)
    total_estoque = sum((p.estoque or 0) for p in produtos)

    lucro_total = 0
    for v in vendas:
        produto = Produto.query.get(v.produto_id)
        if produto:
            custo = produto.custo or 0
            lucro_total += v.total - (custo * v.quantidade)

    return render_template(
        "index.html",
        saldo=saldo,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro_total,
    )

# ================= CLIENTES =================
@app.route("/clientes")
def clientes():
    lista = Cliente.query.all()
    return render_template("clientes.html", clientes=lista)

@app.route("/add_cliente", methods=["POST"])
def add_cliente():
    nome = request.form["nome"]
    telefone = request.form["telefone"]
    local = request.form["local"]

    novo = Cliente(nome=nome, telefone=telefone, local=local)
    db.session.add(novo)
    db.session.commit()

    return redirect(url_for("clientes"))


# ================= PRODUTOS =================
@app.route("/produtos")
def produtos():
    lista = Produto.query.all()
    return render_template("produtos.html", produtos=lista)

@app.route("/add_produto", methods=["POST"])
def add_produto():
    nome = request.form["nome"]
    preco = float(request.form["preco"])
    custo = float(request.form["custo"])
    estoque = int(request.form["estoque"])

    novo = Produto(
        nome=nome,
        preco=preco,
        custo=custo,
        estoque=estoque
    )

    db.session.add(novo)
    db.session.commit()

    return redirect(url_for("produtos"))


@app.route("/venda", methods=["GET", "POST"])
def venda():
    ...
    return render_template(
        "venda.html",
        produtos=Produto.query.all(),
        clientes=Cliente.query.all(),
    )

@app.route("/entrada_estoque", methods=["GET", "POST"])
def entrada_estoque():
    if request.method == "POST":
        produto_id = request.form["produto"]
        quantidade = int(request.form["quantidade"])

        produto = Produto.query.get(produto_id)
        produto.estoque += quantidade

        movimento = MovimentoEstoque(
            produto_id=produto_id,
            tipo="entrada",
            quantidade=quantidade,
            motivo="Entrada manual"
        )

        db.session.add(movimento)
        db.session.commit()

        return redirect(url_for("entrada_estoque"))

    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "entrada_estoque.html",
        produtos=produtos,
        movimentos=movimentos
    )

@app.route("/fiado")
def fiado():
    clientes_lista = Cliente.query.filter(Cliente.divida > 0).all()
    vendas_fiado = Venda.query.filter_by(pago=False).all()

    return render_template(
        "fiado.html",
        clientes=clientes_lista,
        vendas=vendas_fiado
    )

@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():
    saldo = get_saldo()

    if request.method == 'POST':
        tipo = request.form['tipo']
        valor = float(request.form['valor'])
        origem = request.form['origem']
        descricao = request.form['descricao']

        movimento = Movimento(
            tipo=tipo,
            valor=valor,
            origem=origem,
            descricao=descricao
        )

        db.session.add(movimento)

        # Atualiza saldo
        if tipo == 'entrada':
            if origem == 'dinheiro':
                saldo.dinheiro += valor
            else:
                saldo.conta += valor
        else:  # saída
            if origem == 'dinheiro':
                saldo.dinheiro -= valor
            else:
                saldo.conta -= valor

        db.session.commit()
        return redirect(url_for('movimentacao'))

    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    return render_template(
        'movimentacao.html',
        movimentos=movimentos,
        saldo=saldo
    )

@app.route('/relatorio_financeiro')
def relatorio_financeiro():
    saldo = get_saldo()
    movimentos = Movimento.query.all()

    entradas = sum(m.valor for m in movimentos if m.tipo == 'entrada')
    saidas = sum(m.valor for m in movimentos if m.tipo == 'saida')

    return render_template(
        'relatorio_financeiro.html',
        movimentos=movimentos,
        entradas=entradas,
        saidas=saidas,
        saldo=saldo
    )

@app.route("/relatorio_estoque")
def relatorio_estoque():
    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "relatorio_estoque.html",
        produtos=produtos,
        movimentos=movimentos
    )

@app.route("/relatorio_lucro")
def relatorio_lucro():
    return render_template("relatorio_lucro.html")
# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)