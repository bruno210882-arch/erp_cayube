from sqlalchemy import func
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
    produtos_baixo_estoque = Produto.query.filter(Produto.estoque <= 5).all()

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

# ==================VENDA========================
@app.route("/venda", methods=["GET", "POST"])
def venda():
    if request.method == "POST":
        produto_id = int(request.form["produto"])
        cliente_id = int(request.form["cliente"])
        quantidade = int(request.form["quantidade"])
        forma = request.form.get("forma")

        produto = Produto.query.get(produto_id)
        cliente = Cliente.query.get(cliente_id)
        saldo = get_saldo()

        if not produto or not cliente:
            return redirect(url_for("venda"))

        if quantidade <= 0:
            return "Quantidade inválida."

        # VERIFICA ESTOQUE
        if (produto.estoque or 0) < quantidade:
            return "Estoque insuficiente para essa venda."

        total = produto.preco * quantidade

        # DEFINE SE É FIADO OU PAGO
        pago = False if forma == "fiado" else True

        nova_venda = Venda(
            produto_id=produto_id,
            cliente_id=cliente_id,
            quantidade=quantidade,
            total=total,
            pago=pago,
            forma_pagamento=forma
        )

        # ATUALIZA ESTOQUE
        produto.estoque -= quantidade

        mov_estoque = MovimentoEstoque(
            produto_id=produto_id,
            tipo="saida",
            quantidade=quantidade,
            motivo="Venda"
        )

        db.session.add(nova_venda)
        db.session.add(mov_estoque)

        # SE FOI PAGO, ENTRA NO CAIXA
        if pago:
            if forma == "dinheiro":
                saldo.dinheiro += total
            elif forma == "transferencia":
                saldo.conta += total
        else:
            # SE FOR FIADO, AUMENTA DÍVIDA
            cliente.divida = (cliente.divida or 0) + total

        db.session.commit()

        # REDIRECIONAMENTO
        if forma == "fiado":
            return redirect(url_for("fiado"))
        else:
            return redirect(url_for("index"))

    return render_template(
        "venda.html",
        produtos=Produto.query.all(),
        clientes=Cliente.query.all(),
    )
# ==============ENTRADA ESTOQUE=====================
@app.route("/entrada_estoque", methods=["GET", "POST"])
def entrada_estoque():
    saldo = get_saldo()

    if request.method == "POST":
        produto_id = int(request.form["produto"])
        quantidade = int(request.form["quantidade"])
        valor_compra = float(request.form["valor_compra"])
        origem = request.form["origem"]

        produto = Produto.query.get(produto_id)
        if not produto:
            return redirect(url_for("entrada_estoque"))

        if origem == "capital_dinheiro":
            saldo.dinheiro += valor_compra
            db.session.add(Movimento(
                tipo="entrada",
                valor=valor_compra,
                origem="dinheiro",
                descricao="Injeção de capital para compra de estoque"
            ))
            saldo.dinheiro -= valor_compra
            origem_financeira = "dinheiro"

        elif origem == "capital_conta":
            saldo.conta += valor_compra
            db.session.add(Movimento(
                tipo="entrada",
                valor=valor_compra,
                origem="conta",
                descricao="Injeção de capital para compra de estoque"
            ))
            saldo.conta -= valor_compra
            origem_financeira = "conta"

        elif origem == "dinheiro":
            saldo.dinheiro -= valor_compra
            origem_financeira = "dinheiro"

        else:
            saldo.conta -= valor_compra
            origem_financeira = "conta"

        produto.estoque = (produto.estoque or 0) + quantidade

        db.session.add(MovimentoEstoque(
            produto_id=produto_id,
            tipo="entrada",
            quantidade=quantidade,
            motivo="Compra"
        ))

        db.session.add(Movimento(
            tipo="saida",
            valor=valor_compra,
            origem=origem_financeira,
            descricao=f"Compra de estoque: {produto.nome} ({quantidade} un.)"
        ))

        db.session.commit()
        return redirect(url_for("entrada_estoque"))

    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "entrada_estoque.html",
        produtos=Produto.query.all(),
        movimentos=movimentos,
        saldo=saldo
    )
# ======================FIADO================================

from sqlalchemy import func

@app.route("/fiado")
def fiado():
    vendas_fiado = (
        db.session.query(Venda, Cliente, Produto)
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.pago == False)
        .all()
    )

    clientes_resumo = (
        db.session.query(
            Cliente.nome,
            func.sum(Venda.total).label("total_divida")
        )
        .join(Venda, Venda.cliente_id == Cliente.id)
        .filter(Venda.pago == False)
        .group_by(Cliente.nome)
        .all()
    )

    total_geral_fiado = sum(c.total_divida or 0 for c in clientes_resumo)

    return render_template(
        "fiado.html",
        vendas_fiado=vendas_fiado,
        clientes_resumo=clientes_resumo,
        total_geral_fiado=total_geral_fiado
    )
# ===========RECEBER VENDA==================================


@app.route("/receber_venda/<int:venda_id>", methods=["POST"])
def receber_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    cliente = Cliente.query.get(venda.cliente_id)
    saldo = get_saldo()

    forma = request.form["forma"]

    if not venda.pago:
        venda.pago = True
        venda.forma_pagamento = forma

        if forma.lower() == "dinheiro":
            saldo.dinheiro += venda.total
        else:
            saldo.conta += venda.total

        if cliente:
            cliente.divida = max((cliente.divida or 0) - venda.total, 0)

        db.session.commit()

    return redirect(url_for("fiado"))

# ====================MOVIMENTAÇAO==========================

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
# ==================RELATORIO FINANCEIRO==========================
@app.route("/relatorio_financeiro")
def relatorio_financeiro():
    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    entradas = sum(m.valor for m in movimentos if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentos if m.tipo == "saida")

    return render_template(
        "financeiro.html",
        movimentos=movimentos,
        entradas=entradas,
        saidas=saidas,
        saldo=entradas - saidas
    )
# ============relatorio estoque=====================
@app.route("/relatorio_estoque")
def relatorio_estoque():
    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "relatorio_estoque.html",
        produtos=produtos,
        movimentos=movimentos
    )
# ===============RELATORIO LUCRO===============================
@app.route("/relatorio_lucro")
def relatorio_lucro():
    vendas = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .all()
    )

    lucro_total = 0
    relatorio = []

    for venda, produto in vendas:
        custo_total = (produto.custo or 0) * venda.quantidade
        lucro = venda.total - custo_total
        lucro_total += lucro

        relatorio.append({
            "produto": produto.nome,
            "quantidade": venda.quantidade,
            "venda": venda.total,
            "custo": custo_total,
            "lucro": lucro
        })

    return render_template(
        "lucro.html",
        relatorio=relatorio,
        lucro_total=lucro_total
    )
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)