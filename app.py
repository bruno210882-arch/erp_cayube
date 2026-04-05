import os
import io
import re
import base64
from datetime import datetime, date
from functools import wraps
from collections import defaultdict

import qrcode
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cayube_erp_chave_secreta_2026"

# =========================
# CONFIG BANCO
# =========================
uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///erp_cayube.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# PIX CONFIG
# =========================
PIX_CHAVE = "seuemail@pix.com"
PIX_NOME = "CAYUBE"
PIX_CIDADE = "CAMPINAS"

# =========================
# LOGIN OBRIGATÓRIO
# =========================
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
            return redirect(url_for("login_cliente"))
        return f(*args, **kwargs)
    return decorated_function

# =========================
# MODELOS
# =========================
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
    pago = db.Column(db.Boolean, default=False)
    forma_pagamento = db.Column(db.String(20))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status_pedido = db.Column(db.String(30), default="aguardando_aprovacao")
    status_pix = db.Column(db.String(30), default="pendente")


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


with app.app_context():
    db.create_all()

# =========================
# PWA ERP
# =========================
@app.route("/manifest-erp.webmanifest")
def manifest_erp():
    return jsonify({
        "id": "/login",
        "name": "Cayube ERP Gerencial",
        "short_name": "ERP Cayube",
        "description": "ERP gerencial instalável",
        "start_url": "/login",
        "scope": "/",
        "display": "standalone",
        "background_color": "#f4f6f9",
        "theme_color": "#1e1e2f",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icons/erp-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/erp-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })


@app.route("/service-worker.js")
def service_worker():
    js = """
const CACHE_NAME = "cayube-erp-v1";
const URLS_TO_CACHE = ["/login", "/static/logo.png"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).catch(() => caches.match("/login"));
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

# =========================
# PWA CLIENTE
# =========================
@app.route("/manifest-cliente.webmanifest")
def manifest_cliente():
    return jsonify({
        "id": "/cliente/login",
        "name": "Cayube Área do Cliente",
        "short_name": "Cliente Cayube",
        "description": "Portal do cliente instalável",
        "start_url": "/cliente/login",
        "scope": "/cliente",
        "display": "standalone",
        "background_color": "#f4f6f9",
        "theme_color": "#1e1e2f",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icons/cliente-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/cliente-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })


@app.route("/cliente-sw.js")
def cliente_service_worker():
    js = """
const CACHE_NAME = "cayube-cliente-v1";
const URLS_TO_CACHE = [
  "/cliente/login",
  "/cliente",
  "/static/logo.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).catch(() => caches.match("/cliente/login"));
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

# =========================
# FUNÇÕES PIX
# =========================
def crc16(payload):
    polinomio = 0x1021
    resultado = 0xFFFF

    for byte in payload.encode("utf-8"):
        resultado ^= byte << 8
        for _ in range(8):
            if resultado & 0x8000:
                resultado = (resultado << 1) ^ polinomio
            else:
                resultado <<= 1
            resultado &= 0xFFFF

    return format(resultado, "04X")


def campo_pix(id_campo, valor):
    return f"{id_campo}{str(len(valor)).zfill(2)}{valor}"


def gerar_payload_pix(chave, nome, cidade, valor, identificador="***"):
    payload = ""
    payload += campo_pix("00", "01")
    payload += campo_pix("26", campo_pix("00", "br.gov.bcb.pix") + campo_pix("01", chave))
    payload += campo_pix("52", "0000")
    payload += campo_pix("53", "986")
    payload += campo_pix("54", f"{valor:.2f}")
    payload += campo_pix("58", "BR")
    payload += campo_pix("59", nome[:25])
    payload += campo_pix("60", cidade[:15])
    payload += campo_pix("62", campo_pix("05", identificador[:25]))
    payload += "6304"
    payload += crc16(payload)
    return payload


def gerar_qrcode_base64(texto):
    qr = qrcode.make(texto)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# =========================
# ROTAS ADMIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = Usuario.query.filter_by(usuario=request.form["usuario"]).first()
        if usuario and check_password_hash(usuario.senha, request.form["senha"]):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_nivel"] = usuario.nivel
            return redirect(url_for("index"))
        flash("Login inválido")
    return render_template("login.html")


@app.route("/")
@login_obrigatorio
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/clientes")
@login_obrigatorio
def clientes():
    return render_template("clientes.html", clientes=Cliente.query.all())


@app.route("/add_cliente", methods=["POST"])
@login_obrigatorio
def add_cliente():
    nome = request.form["nome"]
    telefone = re.sub(r"\D", "", request.form["telefone"])
    local = request.form["local"]

    novo = Cliente(nome=nome, telefone=telefone, local=local, ativo=True)
    novo.set_senha("123456")

    db.session.add(novo)
    db.session.commit()

    flash("Cliente cadastrado. Senha padrão: 123456", "success")
    return redirect(url_for("clientes"))


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
@login_obrigatorio
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        cliente.nome = request.form["nome"]
        cliente.telefone = re.sub(r"\D", "", request.form["telefone"])
        cliente.local = request.form["local"]
        db.session.commit()
        flash("Cliente atualizado", "success")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/definir_senha_cliente/<int:cliente_id>", methods=["GET", "POST"])
@login_obrigatorio
def definir_senha_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == "POST":
        cliente.set_senha(request.form["senha"])
        db.session.commit()
        return redirect(url_for("clientes"))
    return render_template("definir_senha_cliente.html", cliente=cliente)

# =========================
# LOGIN CLIENTE
# =========================
@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        telefone = re.sub(r"\D", "", request.form["telefone"])
        senha = request.form["senha"]

        cliente = Cliente.query.filter_by(telefone=telefone, ativo=True).first()

        if cliente and cliente.check_senha(senha):
            session["cliente_id"] = cliente.id
            session["cliente_nome"] = cliente.nome
            return redirect(url_for("cliente_dashboard"))

        flash("Telefone ou senha inválidos")

    return render_template("cliente_login.html")


@app.route("/cliente/logout")
def cliente_logout():
    session.pop("cliente_id", None)
    session.pop("cliente_nome", None)
    return redirect(url_for("login_cliente"))


@app.route("/cliente")
@login_cliente_obrigatorio
def cliente_dashboard():
    cliente = Cliente.query.get_or_404(session["cliente_id"])
    return render_template("cliente_dashboard.html", cliente=cliente)

# =========================
# ROTAS DO MENU CLIENTE
# =========================
@app.route("/cliente/estoque")
@login_cliente_obrigatorio
def cliente_estoque():
    produtos = Produto.query.filter(Produto.estoque > 0).all()
    return render_template("cliente_estoque.html", produtos=produtos)


@app.route("/cliente/pedido", methods=["GET", "POST"])
@login_cliente_obrigatorio
def cliente_pedido():
    produtos = Produto.query.filter(Produto.estoque > 0).all()

    if request.method == "POST":
        flash("Pedido enviado com sucesso.", "success")
        return redirect(url_for("cliente_dashboard"))

    return render_template("cliente_pedido.html", produtos=produtos)


@app.route("/cliente/historico")
@login_cliente_obrigatorio
def cliente_historico():
    pedidos = Venda.query.filter_by(cliente_id=session["cliente_id"]).order_by(Venda.data.desc()).all()
    return render_template("cliente_historico.html", pedidos=pedidos)


@app.route("/cliente/itens_em_aberto")
@login_cliente_obrigatorio
def cliente_itens_em_aberto():
    itens_abertos = Venda.query.filter_by(cliente_id=session["cliente_id"], pago=False).order_by(Venda.data.desc()).all()
    total_aberto = sum((item.total or 0) for item in itens_abertos)

    return render_template(
        "cliente_itens_em_aberto.html",
        itens_abertos=itens_abertos,
        total_aberto=total_aberto
    )


@app.route("/cliente/pix")
@login_cliente_obrigatorio
def cliente_pix():
    cliente = Cliente.query.get_or_404(session["cliente_id"])

    pedido = (
        Venda.query
        .filter_by(cliente_id=cliente.id, status_pedido="aprovado", status_pix="pendente")
        .order_by(Venda.data.desc())
        .first()
    )

    if not pedido:
        flash("Você não possui pedido aprovado aguardando pagamento PIX.", "warning")
        return redirect(url_for("cliente_dashboard"))

    payload = gerar_payload_pix(PIX_CHAVE, PIX_NOME, PIX_CIDADE, pedido.total, f"PED{pedido.id}")
    qr = gerar_qrcode_base64(payload)

    return render_template(
        "cliente_pix.html",
        cliente=cliente,
        pedido=pedido,
        valor_aberto=pedido.total,
        payload_pix=payload,
        qr_code_base64=qr
    )


@app.route("/cliente/pix_divida")
@login_cliente_obrigatorio
def cliente_pix_divida():
    cliente = Cliente.query.get_or_404(session["cliente_id"])
    valor = cliente.divida or 0

    if valor <= 0:
        flash("Você não possui valores em aberto.", "warning")
        return redirect(url_for("cliente_dashboard"))

    payload = gerar_payload_pix(PIX_CHAVE, PIX_NOME, PIX_CIDADE, valor, f"DIV{cliente.id}")
    qr = gerar_qrcode_base64(payload)

    return render_template(
        "cliente_pix_divida.html",
        cliente=cliente,
        valor_aberto=valor,
        payload_pix=payload,
        qr_code_base64=qr
    )

# =========================
# UTILIDADES
# =========================
@app.route("/criar_admin")
def criar_admin():
    if Usuario.query.filter_by(usuario="admin").first():
        return "Admin já existe"

    admin = Usuario(
        nome="Administrador",
        usuario="admin",
        senha=generate_password_hash("123456"),
        nivel="admin"
    )

    db.session.add(admin)
    db.session.commit()
    return "Admin criado: admin / 123456"


@app.route("/resetar_senha_clientes")
def resetar_senha_clientes():
    for c in Cliente.query.all():
        c.set_senha("123456")
    db.session.commit()
    return "Senhas resetadas"


@app.route("/atualizar_banco")
def atualizar_banco():
    db.create_all()
    return "Banco atualizado"


if __name__ == "__main__":
    app.run(debug=True)