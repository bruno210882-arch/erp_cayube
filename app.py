import os
import subprocess
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cayube_erp_chave_secreta"

# CONFIG BANCO RENDER
uri = os.getenv("DATABASE_URL")

if not uri:
    raise RuntimeError("DATABASE_URL não configurado no Render!")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------------
# LOGIN OBRIGATÓRIO
# ------------------------
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------
# MODELS
# ------------------------

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    telefone = db.Column(db.String(50))
    local = db.Column(db.String(100))

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
    data = db.Column(db.DateTime, default=datetime.utcnow)

class MovimentacaoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer)
    tipo = db.Column(db.String(20))
    quantidade = db.Column(db.Integer)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Caixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))  # entrada / saida
    valor = db.Column(db.Float)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    usuario = db.Column(db.String(50), unique=True)
    senha = db.Column(db.String(200))
    nivel = db.Column(db.String(20))  # admin ou funcionario

# ------------------------
# LOGIN
# ------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = Usuario.query.filter_by(usuario=request.form["usuario"]).first()

        if usuario and check_password_hash(usuario.senha, request.form["senha"]):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_nivel"] = usuario.nivel
            return redirect(url_for("index"))
        else:
            flash("Usuário ou senha inválidos")

    return render_template("login.html")

# ------------------------
# DASHBOARD
# ------------------------
@app.route("/")
@login_obrigatorio
def index():
    dinheiro = db.session.query(func.sum(Caixa.valor)).filter(Caixa.tipo == "entrada").scalar() or 0
    saida = db.session.query(func.sum(Caixa.valor)).filter(Caixa.tipo == "saida").scalar() or 0

    saldo = dinheiro - saida

    total_vendas = db.session.query(func.sum(Venda.total)).scalar() or 0
    total_fiado = db.session.query(func.sum(Venda.total)).filter(Venda.pago == False).scalar() or 0
    total_estoque = db.session.query(func.sum(Produto.estoque)).scalar() or 0

    lucro = db.session.query(func.sum((Produto.preco - Produto.custo) * Venda.quantidade)).join(Produto).scalar() or 0

    return render_template(
        "index.html",
        saldo={"dinheiro": saldo, "conta": 0},
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        total_estoque=total_estoque,
        lucro_total=lucro
    )

# ------------------------
# CLIENTES
# ------------------------
@app.route("/clientes", methods=["GET", "POST"])
@login_obrigatorio
def clientes():
    if request.method == "POST":
        novo = Cliente(
            nome=request.form["nome"],
            telefone=request.form["telefone"],
            local=request.form["local"]
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("clientes"))

    return render_template("clientes.html", clientes=Cliente.query.all())

# ------------------------
# PRODUTOS
# ------------------------
@app.route("/produtos", methods=["GET", "POST"])
@login_obrigatorio
def produtos():
    if request.method == "POST":
        novo = Produto(
            nome=request.form["nome"],
            preco=float(request.form["preco"]),
            custo=float(request.form["custo"]),
            estoque=int(request.form["estoque"])
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for("produtos"))

    return render_template("produtos.html", produtos=Produto.query.all())

# ------------------------
# VENDA
# ------------------------
@app.route("/venda", methods=["GET", "POST"])
@login_obrigatorio
def venda():
    if request.method == "POST":
        produto = Produto.query.get(request.form["produto"])
        cliente = Cliente.query.get(request.form["cliente"])
        quantidade = int(request.form["quantidade"])
        forma = request.form["forma_pagamento"]

        total = produto.preco * quantidade

        venda = Venda(
            produto_id=produto.id,
            cliente_id=cliente.id,
            quantidade=quantidade,
            total=total,
            pago=(forma != "fiado"),
            forma_pagamento=forma
        )

        produto.estoque -= quantidade

        if forma != "fiado":
            caixa = Caixa(tipo="entrada", valor=total, motivo="Venda")
            db.session.add(caixa)

        mov = MovimentacaoEstoque(
            produto_id=produto.id,
            tipo="saida",
            quantidade=quantidade,
            motivo="Venda"
        )

        db.session.add(venda)
        db.session.add(mov)
        db.session.commit()

        return redirect(url_for("venda"))

    return render_template(
        "venda.html",
        produtos=Produto.query.all(),
        clientes=Cliente.query.all()
    )

# ------------------------
# FIADO
# ------------------------
@app.route("/fiado")
@login_obrigatorio
def fiado():
    vendas = Venda.query.filter_by(pago=False).all()
    return render_template("fiado.html", vendas=vendas)

@app.route("/receber/<int:id>")
@login_obrigatorio
def receber(id):
    venda = Venda.query.get(id)
    venda.pago = True

    caixa = Caixa(tipo="entrada", valor=venda.total, motivo="Recebimento Fiado")
    db.session.add(caixa)
    db.session.commit()

    return redirect(url_for("fiado"))

# ------------------------
# ENTRADA ESTOQUE (COMPRA)
# ------------------------
@app.route("/entrada_estoque", methods=["GET", "POST"])
@login_obrigatorio
def entrada_estoque():
    if request.method == "POST":
        produto = Produto.query.get(request.form["produto"])
        quantidade = int(request.form["quantidade"])
        valor = float(request.form["valor"])

        produto.estoque += quantidade

        mov = MovimentacaoEstoque(
            produto_id=produto.id,
            tipo="entrada",
            quantidade=quantidade,
            motivo="Compra"
        )

        caixa = Caixa(tipo="saida", valor=valor, motivo="Compra de estoque")

        db.session.add(mov)
        db.session.add(caixa)
        db.session.commit()

        return redirect(url_for("entrada_estoque"))

    return render_template("entrada_estoque.html", produtos=Produto.query.all())

# ------------------------
# RELATÓRIOS
# ------------------------
@app.route("/relatorio_estoque")
@login_obrigatorio
def relatorio_estoque():
    return render_template(
        "relatorio_estoque.html",
        produtos=Produto.query.all(),
        movimentos=MovimentacaoEstoque.query.all()
    )

@app.route("/relatorio_financeiro")
@login_obrigatorio
def relatorio_financeiro():
    caixa = Caixa.query.all()
    return render_template("relatorio_financeiro.html", caixa=caixa)

@app.route("/relatorio_lucro")
@login_obrigatorio
def relatorio_lucro():
    vendas = Venda.query.all()
    return render_template("relatorio_lucro.html", vendas=vendas)

# ------------------------
# BACKUP
# ------------------------
@app.route("/backup")
@login_obrigatorio
def backup():
    filename = "backup.sql"
    comando = f'pg_dump "{uri}" > {filename}'
    os.system(comando)
    return send_file(filename, as_attachment=True)

# ------------------------
# CRIAR TABELAS
# ------------------------
@app.route("/criar_tabelas")
def criar_tabelas():
    db.create_all()
    return "Tabelas criadas!"

# ------------------------
# APAGAR BANCO
# ------------------------
# @app.route("/resetar_banco")
# def resetar_banco():
#    db.drop_all()
#    db.create_all()
#    return "Banco resetado com sucesso!" 
# ------------------------
# USUARIO
# ------------------------

@app.route("/usuarios", methods=["GET", "POST"])
@login_obrigatorio
def usuarios():
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    if request.method == "POST":
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

    lista = Usuario.query.all()
    return render_template("usuarios.html", usuarios=lista)
# ------------------------
# ALTERAR SENHA
# ------------------------

@app.route("/alterar_senha/<int:id>", methods=["POST"])
@login_obrigatorio
def alterar_senha(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    usuario.senha = generate_password_hash(request.form["nova_senha"])
    db.session.commit()

    return redirect(url_for("usuarios"))
# ------------------------
# EXCLUIR USUARIO
# ------------------------

@app.route("/excluir_usuario/<int:id>")
@login_obrigatorio
def excluir_usuario(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()

    return redirect(url_for("usuarios"))


@app.route("/criar_admin")
def criar_admin():
    if Usuario.query.filter_by(usuario="admin").first():
        return "Admin já existe"

    senha = generate_password_hash("123456")

    admin = Usuario(
        nome="Administrador",
        usuario="admin",
        senha=senha,
        nivel="admin"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin criado: admin / 123456"
# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)