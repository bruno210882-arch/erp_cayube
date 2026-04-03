import os
import subprocess
from datetime import datetime, date
from functools import wraps
from collections import defaultdict

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cayube_erp_chave_secreta_2026"

# ================= DATABASE =================
uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///erp_cayube.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ================= LOGIN OBRIGATÓRIO =================
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def login_cliente_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cliente_id" not in session:
            flash("Faça login para acessar a área do cliente.", "danger")
            return redirect(url_for("login_cliente"))
        return f(*args, **kwargs)
    return decorated_function


# ================= MODELS =================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    usuario = db.Column(db.String(50), unique=True)
    senha = db.Column(db.String(200))
    nivel = db.Column(db.String(20))


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    local = db.Column(db.String(100))
    divida = db.Column(db.Float, default=0)
    telefone = db.Column(db.String(20), unique=True)
    senha_hash = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, senha)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    custo = db.Column(db.Float, default=0)
    estoque = db.Column(db.Integer, default=0)


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Boolean, default=True)
    forma_pagamento = db.Column(db.String(20))
    data = db.Column(db.DateTime, default=datetime.utcnow)


class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dinheiro = db.Column(db.Float, default=0)
    conta = db.Column(db.Float, default=0)


class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # entrada / saida
    valor = db.Column(db.Float, nullable=False)
    origem = db.Column(db.String(20), nullable=False)  # dinheiro / conta
    descricao = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.utcnow)


class MovimentoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada / saida
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)


class FechamentoCaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    saldo_inicial = db.Column(db.Float, default=0)
    entradas = db.Column(db.Float, default=0)
    saidas = db.Column(db.Float, default=0)
    saldo_final = db.Column(db.Float, default=0)
    observacao = db.Column(db.String(200))


# ================= INIT DB =================
with app.app_context():
    db.create_all()


# ================= FUNÇÕES AUXILIARES =================
def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_digitado = request.form["usuario"]
        senha_digitada = request.form["senha"]

        usuario = Usuario.query.filter_by(usuario=usuario_digitado).first()

        if usuario and check_password_hash(usuario.senha, senha_digitada):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_nivel"] = usuario.nivel
            return redirect(url_for("index"))

        flash("Usuário ou senha inválidos.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/criar_tabelas")
def criar_tabelas():
    db.create_all()
    return "Tabelas criadas com sucesso!"


@app.route("/criar_admin")
def criar_admin():
    if Usuario.query.filter_by(usuario="admin").first():
        return "Admin já existe"

    senha_hash = generate_password_hash("123456")

    admin = Usuario(
        nome="Administrador",
        usuario="admin",
        senha=senha_hash,
        nivel="admin"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin criado com sucesso! Usuario: admin | Senha: 123456"


# ================= DASHBOARD =================
@app.route("/")
@login_obrigatorio
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

    produtos_baixo_estoque = Produto.query.filter(Produto.estoque <= 5).all()

    return render_template(
        "index.html",
        saldo=saldo,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro_total,
        produtos_baixo_estoque=produtos_baixo_estoque
    )


# ================= CLIENTES =================
@app.route("/clientes")
@login_obrigatorio
def clientes():
    lista = Cliente.query.all()
    return render_template("clientes.html", clientes=lista)


@app.route("/add_cliente", methods=["POST"])
@login_obrigatorio
def add_cliente():
    try:
        novo = Cliente(
            nome=request.form["nome"],
            telefone=request.form.get("telefone", "").strip(),
            local=request.form.get("local", "").strip(),
            ativo=True
        )

        # senha padrão inicial
        novo.set_senha("123456")

        db.session.add(novo)
        db.session.commit()
        flash("Cliente cadastrado com sucesso. Senha padrão: 123456", "success")
        return redirect(url_for("clientes"))

    except Exception as e:
        db.session.rollback()
        return f"Erro ao cadastrar cliente: {str(e)}"


@app.route("/excluir_cliente/<int:id>")
@login_obrigatorio
def excluir_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
    return redirect(url_for("clientes"))


@app.route("/definir_senha_cliente/<int:cliente_id>", methods=["GET", "POST"])
@login_obrigatorio
def definir_senha_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == "POST":
        senha = request.form.get("senha", "").strip()

        if not senha:
            flash("Digite uma senha válida.", "danger")
            return redirect(url_for("definir_senha_cliente", cliente_id=cliente.id))

        cliente.set_senha(senha)
        db.session.commit()
        flash("Senha definida com sucesso.", "success")
        return redirect(url_for("clientes"))

    return render_template("definir_senha_cliente.html", cliente=cliente)


# ================= PRODUTOS =================
@app.route("/produtos")
@login_obrigatorio
def produtos():
    lista = Produto.query.all()
    return render_template("produtos.html", produtos=lista)


@app.route("/add_produto", methods=["POST"])
@login_obrigatorio
def add_produto():
    try:
        novo = Produto(
            nome=request.form["nome"],
            preco=float(request.form["preco"]),
            custo=float(request.form["custo"]),
            estoque=int(request.form["estoque"])
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("produtos"))
    except Exception as e:
        db.session.rollback()
        return f"Erro ao cadastrar produto: {str(e)}"


@app.route("/excluir_produto/<int:id>")
@login_obrigatorio
def excluir_produto(id):
    produto = Produto.query.get(id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return redirect(url_for("produtos"))


# ================= VENDA =================
@app.route("/venda", methods=["GET", "POST"])
@login_obrigatorio
def venda():
    if request.method == "POST":
        try:
            produto_id = int(request.form["produto"])
            cliente_id = int(request.form["cliente"])
            quantidade = int(request.form["quantidade"])
            forma = request.form.get("forma")

            produto = Produto.query.get(produto_id)
            cliente = Cliente.query.get(cliente_id)
            saldo = get_saldo()

            if not produto:
                return "Produto não encontrado."

            if not cliente:
                return "Cliente não encontrado."

            if quantidade <= 0:
                return "Quantidade inválida."

            if (produto.estoque or 0) < quantidade:
                return "Estoque insuficiente para essa venda."

            total = produto.preco * quantidade
            pago = False if forma == "fiado" else True

            nova_venda = Venda(
                produto_id=produto_id,
                cliente_id=cliente_id,
                quantidade=quantidade,
                total=total,
                pago=pago,
                forma_pagamento=forma
            )

            produto.estoque -= quantidade

            mov_estoque = MovimentoEstoque(
                produto_id=produto_id,
                tipo="saida",
                quantidade=quantidade,
                motivo="Venda"
            )

            db.session.add(nova_venda)
            db.session.add(mov_estoque)

            if pago:
                if forma == "dinheiro":
                    saldo.dinheiro += total
                elif forma == "transferencia":
                    saldo.conta += total
            else:
                cliente.divida = (cliente.divida or 0) + total

            db.session.commit()

            if forma == "fiado":
                return redirect(url_for("fiado"))
            return redirect(url_for("index"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar venda: {str(e)}"

    return render_template(
        "venda.html",
        produtos=Produto.query.all(),
        clientes=Cliente.query.all(),
    )


# ================= FIADO =================
@app.route("/fiado")
@login_obrigatorio
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


@app.route("/receber_venda/<int:venda_id>", methods=["POST"])
@login_obrigatorio
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


# ================= MOVIMENTAÇÃO / CAIXA =================
@app.route("/movimentacao", methods=["GET", "POST"])
@login_obrigatorio
def movimentacao():
    saldo = get_saldo()

    if request.method == "POST":
        try:
            tipo = request.form["tipo"]
            valor = float(request.form["valor"])
            origem = request.form["origem"]
            descricao = request.form["descricao"]

            if tipo == "entrada":
                if origem == "dinheiro":
                    saldo.dinheiro += valor
                else:
                    saldo.conta += valor
            else:
                if origem == "dinheiro":
                    saldo.dinheiro -= valor
                else:
                    saldo.conta -= valor

            movimento = Movimento(
                tipo=tipo,
                valor=valor,
                origem=origem,
                descricao=descricao
            )

            db.session.add(movimento)
            db.session.commit()
            return redirect(url_for("movimentacao"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar movimentação: {str(e)}"

    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    return render_template(
        "movimentacao.html",
        movimentos=movimentos,
        saldo=saldo
    )


# ================= ENTRADA DE ESTOQUE =================
@app.route("/entrada_estoque", methods=["GET", "POST"])
@login_obrigatorio
def entrada_estoque():
    saldo = get_saldo()

    if request.method == "POST":
        try:
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

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar entrada de estoque: {str(e)}"

    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "entrada_estoque.html",
        produtos=Produto.query.all(),
        movimentos=movimentos,
        saldo=saldo
    )


# ================= RELATÓRIO FINANCEIRO =================
@app.route("/relatorio_financeiro")
@login_obrigatorio
def relatorio_financeiro():
    saldo = get_saldo()
    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    total_entradas = sum(m.valor for m in movimentos if m.tipo == "entrada")
    total_saidas = sum(m.valor for m in movimentos if m.tipo == "saida")

    return render_template(
        "relatorio_financeiro.html",
        saldo=saldo,
        movimentos=movimentos,
        entradas=total_entradas,
        saidas=total_saidas
    )


# ================= RELATÓRIO ESTOQUE =================
@app.route("/relatorio_estoque")
@login_obrigatorio
def relatorio_estoque():
    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "relatorio_estoque.html",
        produtos=produtos,
        movimentos=movimentos
    )


# ================= RELATÓRIO LUCRO =================
@app.route("/relatorio_lucro")
@login_obrigatorio
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
            "produto": p.nome,
            "vendido": total_vendido,
            "faturamento": faturamento,
            "custo": custo_total,
            "lucro": lucro
        })

    return render_template("relatorio_lucro.html", relatorio=relatorio)


# ================= FLUXO DE CAIXA =================
@app.route("/fluxo_caixa")
@login_obrigatorio
def fluxo_caixa():
    movimentos = Movimento.query.order_by(Movimento.data.desc()).all()

    fluxo_por_dia = defaultdict(lambda: {"entradas": 0, "saidas": 0})

    for m in movimentos:
        dia = m.data.date()
        if m.tipo == "entrada":
            fluxo_por_dia[dia]["entradas"] += m.valor
        elif m.tipo == "saida":
            fluxo_por_dia[dia]["saidas"] += m.valor

    relatorio = []
    for dia, valores in fluxo_por_dia.items():
        saldo_dia = valores["entradas"] - valores["saidas"]
        relatorio.append({
            "data": dia,
            "entradas": valores["entradas"],
            "saidas": valores["saidas"],
            "saldo": saldo_dia
        })

    relatorio.sort(key=lambda x: x["data"], reverse=True)

    return render_template("fluxo_caixa.html", relatorio=relatorio)


# ================= FECHAMENTO DE CAIXA =================
@app.route("/fechamento_caixa", methods=["GET", "POST"])
@login_obrigatorio
def fechamento_caixa():
    hoje = date.today()
    saldo = get_saldo()

    movimentos_hoje = Movimento.query.filter(
        db.func.date(Movimento.data) == hoje
    ).all()

    entradas = sum(m.valor for m in movimentos_hoje if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentos_hoje if m.tipo == "saida")
    saldo_final = (saldo.dinheiro or 0) + (saldo.conta or 0)

    fechamento_existente = FechamentoCaixa.query.filter_by(data=hoje).first()

    if request.method == "POST":
        try:
            observacao = request.form.get("observacao", "")
            saldo_inicial = float(request.form.get("saldo_inicial", 0))

            if fechamento_existente:
                fechamento_existente.saldo_inicial = saldo_inicial
                fechamento_existente.entradas = entradas
                fechamento_existente.saidas = saidas
                fechamento_existente.saldo_final = saldo_final
                fechamento_existente.observacao = observacao
            else:
                novo = FechamentoCaixa(
                    data=hoje,
                    saldo_inicial=saldo_inicial,
                    entradas=entradas,
                    saidas=saidas,
                    saldo_final=saldo_final,
                    observacao=observacao
                )
                db.session.add(novo)

            db.session.commit()
            return redirect(url_for("fechamento_caixa"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar fechamento de caixa: {str(e)}"

    return render_template(
        "fechamento_caixa.html",
        hoje=hoje,
        entradas=entradas,
        saidas=saidas,
        saldo_final=saldo_final,
        fechamento=fechamento_existente
    )


# ================= USUÁRIOS =================
@app.route("/usuarios", methods=["GET", "POST"])
@login_obrigatorio
def usuarios():
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        try:
            nome = request.form["nome"]
            usuario = request.form["usuario"]
            senha = generate_password_hash(request.form["senha"])
            nivel = request.form["nivel"]

            novo = Usuario(
                nome=nome,
                usuario=usuario,
                senha=senha,
                nivel=nivel
            )

            db.session.add(novo)
            db.session.commit()
            return redirect(url_for("usuarios"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar usuário: {str(e)}"

    lista = Usuario.query.all()
    return render_template("usuarios.html", usuarios=lista)


@app.route("/alterar_senha/<int:id>", methods=["POST"])
@login_obrigatorio
def alterar_senha(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.senha = generate_password_hash(request.form["nova_senha"])
        db.session.commit()

    return redirect(url_for("usuarios"))


@app.route("/excluir_usuario/<int:id>")
@login_obrigatorio
def excluir_usuario(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for("usuarios"))

@app.route("/atualizar_banco")
def atualizar_banco():
    from sqlalchemy import text

    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE cliente ADD COLUMN IF NOT EXISTS senha_hash VARCHAR(255)"))
            conn.execute(text("ALTER TABLE cliente ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE"))
            conn.commit()

        return "Banco atualizado com sucesso!"

    except Exception as e:
        return f"Erro ao atualizar banco: {str(e)}"
# ================= BACKUP =================
@app.route("/backup")
@login_obrigatorio
def backup():
    try:
        current_uri = os.getenv("DATABASE_URL")

        if not current_uri:
            return "Backup disponível apenas no ambiente com PostgreSQL."

        if current_uri.startswith("postgres://"):
            current_uri = current_uri.replace("postgres://", "postgresql://", 1)

        filename = "backup.sql"
        comando = f'pg_dump "{current_uri}" > {filename}'
        os.system(comando)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Erro ao gerar backup: {str(e)}"


# ================= ÁREA DO CLIENTE =================
@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        telefone = request.form.get("telefone", "").strip()
        senha = request.form.get("senha", "").strip()

        cliente = Cliente.query.filter_by(telefone=telefone, ativo=True).first()

        if cliente and cliente.check_senha(senha):
            session["cliente_id"] = cliente.id
            session["cliente_nome"] = cliente.nome
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("cliente_dashboard"))
        else:
            flash("Telefone ou senha inválidos.", "danger")

    return render_template("cliente_login.html")


@app.route("/cliente/logout")
def cliente_logout():
    session.pop("cliente_id", None)
    session.pop("cliente_nome", None)
    flash("Você saiu da área do cliente.", "success")
    return redirect(url_for("login_cliente"))


@app.route("/cliente")
@login_cliente_obrigatorio
def cliente_dashboard():
    cliente = Cliente.query.get_or_404(session["cliente_id"])

    pedidos = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.cliente_id == cliente.id)
        .order_by(Venda.data.desc())
        .all()
    )

    total_pedidos = sum((venda.total or 0) for venda, _produto in pedidos)
    total_aberto = cliente.divida or 0

    return render_template(
        "cliente_dashboard.html",
        cliente=cliente,
        pedidos=pedidos,
        total_pedidos=total_pedidos,
        total_aberto=total_aberto
    )


@app.route("/cliente/estoque")
@login_cliente_obrigatorio
def cliente_estoque():
    produtos = Produto.query.filter(Produto.estoque > 0).all()
    return render_template("cliente_estoque.html", produtos=produtos)


@app.route("/cliente/pedido", methods=["GET", "POST"])
@login_cliente_obrigatorio
def cliente_pedido():
    cliente = Cliente.query.get_or_404(session["cliente_id"])
    produtos = Produto.query.filter(Produto.estoque > 0).all()

    if request.method == "POST":
        try:
            produto_id = int(request.form["produto"])
            quantidade = int(request.form["quantidade"])

            produto = Produto.query.get_or_404(produto_id)

            if quantidade <= 0:
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("cliente_pedido"))

            if produto.estoque < quantidade:
                flash("Estoque insuficiente.", "danger")
                return redirect(url_for("cliente_pedido"))

            total = (produto.preco or 0) * quantidade

            nova = Venda(
                produto_id=produto.id,
                cliente_id=cliente.id,
                quantidade=quantidade,
                total=total,
                pago=False,
                forma_pagamento="pedido_cliente",
                data=datetime.utcnow()
            )

            produto.estoque -= quantidade
            cliente.divida = (cliente.divida or 0) + total

            mov_estoque = MovimentoEstoque(
                produto_id=produto.id,
                tipo="saida",
                quantidade=quantidade,
                motivo="Pedido do cliente"
            )

            db.session.add(nova)
            db.session.add(mov_estoque)
            db.session.commit()

            flash("Pedido realizado com sucesso.", "success")
            return redirect(url_for("cliente_dashboard"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar pedido do cliente: {str(e)}"

    return render_template("cliente_pedido.html", produtos=produtos)


@app.route("/cliente/historico")
@login_cliente_obrigatorio
def cliente_historico():
    cliente = Cliente.query.get_or_404(session["cliente_id"])

    pedidos = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.cliente_id == cliente.id)
        .order_by(Venda.data.desc())
        .all()
    )

    return render_template(
        "cliente_historico.html",
        cliente=cliente,
        pedidos=pedidos
    )


# ================= RESET =================
@app.route("/resetar_banco")
@login_obrigatorio
def resetar_banco():
    db.drop_all()
    db.create_all()
    return "Banco resetado com sucesso!"


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)