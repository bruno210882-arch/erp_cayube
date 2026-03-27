from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# 🔥 CONFIGURAÇÃO DO BANCO (CORRETO)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:Flexis150300@db.izcbwtvcfszrctsxoenm.supabase.co:5432/postgres"
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
    custo = db.Column(db.Float)  # 👈 NOVO
    estoque = db.Column(db.Integer)


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer)
    cliente_id = db.Column(db.Integer)
    quantidade = db.Column(db.Integer)
    total = db.Column(db.Float)
    pago = db.Column(db.Boolean)
    forma_pagamento = db.Column(db.String(20))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))	
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))


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


# ================= ROTAS =================

@app.route('/')
def index():

    saldo = get_saldo()

    vendas = Venda.query.all()
    produtos = Produto.query.all()
    clientes = Cliente.query.all()

    total_vendas = sum(v.total for v in vendas if v.pago)
    total_fiado = sum(v.total for v in vendas if not v.pago)
    total_estoque = sum(p.estoque for p in produtos)

    lucro_total = 0
    for v in vendas:
        produto = Produto.query.get(v.produto_id)
        if produto:
            custo = produto.custo or 0
            lucro_total += (v.total - (custo * v.quantidade))

    return render_template(
        'index.html',
        saldo=saldo,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro_total
    )

# ===== CLIENTES =====

@app.route('/clientes')
def clientes():
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)


@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    nome = request.form['nome']
    telefone = request.form.get('telefone')

    novo = Cliente(nome=nome, telefone=telefone)

    db.session.add(novo)
    db.session.commit()

    return redirect(url_for('clientes'))


# ===== PRODUTOS =====

@app.route('/produtos')
def produtos():
    lista = Produto.query.all()
    return render_template('produtos.html', produtos=lista)


@app.route('/add_produto', methods=['POST'])
def add_produto():
    nome = request.form['nome']
    preco = float(request.form['preco'])
    custo = float(request.form['custo'])  # 👈 NOVO
    estoque = int(request.form['estoque'])

    novo = Produto(
        nome=nome,
        preco=preco,
        custo=custo,   # 👈 SALVANDO
        estoque=estoque
    )

    db.session.add(novo)
    db.session.commit()

    return redirect('/produtos')

# ===== VENDA =====

@app.route('/venda', methods=['GET', 'POST'])
def venda():

    if request.method == 'POST':
        produto_id = int(request.form['produto'])
        cliente_id = int(request.form['cliente'])
        quantidade = int(request.form['quantidade'])
        forma = request.form.get('forma')

        produto = Produto.query.get(produto_id)
        cliente = Cliente.query.get(cliente_id)
        saldo = get_saldo()

        total = produto.preco * quantidade
        pago = False if forma == 'fiado' else True

        nova = Venda(
            produto_id=produto_id,
            cliente_id=cliente_id,
            quantidade=quantidade,
            total=total,
            pago=pago,
            forma_pagamento=forma
        )

        # 💰 Atualiza saldo
        if pago:
            if forma == 'dinheiro':
                saldo.dinheiro += total
            elif forma == 'transferencia':
                saldo.conta += total
        else:
            # 💳 VENDA FIADO → AUMENTA DÍVIDA
            cliente.divida += total

        # 📦 Atualiza estoque
        produto.estoque -= quantidade

        # 📦 Movimento estoque
        mov = MovimentoEstoque(
            produto_id=produto_id,
            tipo='saida',
            quantidade=quantidade,
            motivo='Venda'
        )

        db.session.add(nova)
        db.session.add(mov)
        db.session.commit()

        return redirect('/')

    return render_template(
        'venda.html',
        produtos=Produto.query.all(),
        clientes=Cliente.query.all()
    )


# ===== FIADO =====

@app.route('/fiado')
def fiado():
    clientes = Cliente.query.filter(Cliente.divida > 0).all()
    return render_template('fiado.html', clientes=clientes)


@app.route('/receber/<nome>', methods=['GET', 'POST'])
def receber(nome):
    cliente = Cliente.query.filter_by(nome=nome).first()
    saldo = get_saldo()

    if request.method == 'POST':
        forma = request.form['forma']

        vendas = Venda.query.filter_by(cliente_id=cliente.id, pago=False).all()

        for v in vendas:
            v.pago = True
            v.forma_pagamento = forma

            if forma == 'Dinheiro':
                saldo.dinheiro += v.total
            else:
                saldo.conta += v.total

        db.session.commit()
        return redirect('/fiado')

    return render_template('receber.html', cliente=cliente)


# ===== MOVIMENTAÇÃO FINANCEIRA =====

@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():

    saldo = get_saldo()

    if request.method == 'POST':
        tipo = request.form['tipo']
        valor = float(request.form['valor'])
        origem = request.form['origem']
        descricao = request.form['descricao']

        if tipo == 'entrada':
            if origem == 'dinheiro':
                saldo.dinheiro += valor
            else:
                saldo.conta += valor
        else:
            if origem == 'dinheiro':
                saldo.dinheiro -= valor
            else:
                saldo.conta -= valor

        mov = Movimento(
            tipo=tipo,
            valor=valor,
            origem=origem,
            descricao=descricao
        )

        db.session.add(mov)
        db.session.commit()

        return redirect('/movimentacao')

    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    return render_template(
        'movimentacao.html',
        movimentos=movimentos,
        saldo=saldo
    )


# ===== ENTRADA DE ESTOQUE =====

@app.route('/entrada_estoque', methods=['GET', 'POST'])
def entrada_estoque():

    if request.method == 'POST':
        produto_id = int(request.form['produto'])
        quantidade = int(request.form['quantidade'])

        produto = Produto.query.get(produto_id)
        produto.estoque += quantidade

        mov = MovimentoEstoque(
            produto_id=produto_id,
            tipo='entrada',
            quantidade=quantidade,
            motivo='Compra'
        )

        db.session.add(mov)
        db.session.commit()

        return redirect('/produtos')

    return render_template(
        'entrada_estoque.html',
        produtos=Produto.query.all()
    )

#=============RELATORIO FINANCEIRO=========
@app.route('/relatorio_financeiro')
def relatorio_financeiro():
    saldo = get_saldo()
    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    total_entradas = sum(m.valor for m in movimentos if m.tipo == 'entrada')
    total_saidas = sum(m.valor for m in movimentos if m.tipo == 'saida')

    return render_template(
        'relatorio_financeiro.html',
        saldo=saldo,
        movimentos=movimentos,
        entradas=total_entradas,
        saidas=total_saidas
    )

#=========Relatorio Estoque==============
@app.route('/relatorio_estoque')
def relatorio_estoque():
    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        'relatorio_estoque.html',
        produtos=produtos,
        movimentos=movimentos
    )

#============relatorio lucro============
@app.route('/relatorio_lucro')
def relatorio_lucro():

    produtos = Produto.query.all()
    vendas = Venda.query.all()

    relatorio = []

    for p in produtos:
        vendas_produto = [v for v in vendas if v.produto_id == p.id]

        total_vendido = sum(v.quantidade for v in vendas_produto)
        faturamento = sum(v.total for v in vendas_produto)
        custo_total = total_vendido * (p.custo or 0)

        lucro = faturamento - custo_total

        relatorio.append({
            'produto': p.nome,
            'vendido': total_vendido,
            'faturamento': faturamento,
            'custo': custo_total,
            'lucro': lucro
        })

    return render_template('relatorio_lucro.html', relatorio=relatorio)

# ================= RUN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # CRIA TODAS AS TABEL