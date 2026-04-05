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

PIX_CHAVE = "seuemail@pix.com"
PIX_NOME = "CAYUBE"
PIX_CIDADE = "CAMPINAS"

# =========================
# BANCO
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
        "start_url": "/login",
        "scope": "/",
        "display": "standalone",
        "background_color": "#f4f6f9",
        "theme_color": "#1e1e2f",
        "icons": [
            {"src": "/static/icons/erp-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/erp-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })


@app.route("/service-worker.js")
def service_worker():
    js = """
const CACHE_NAME = "erp-v1";
const URLS_TO_CACHE = ["/login"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

# =========================
# LOGIN ADMIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.clear()

    if request.method == "POST":
        usuario = Usuario.query.filter_by(usuario=request.form["usuario"]).first()
        if usuario and check_password_hash(usuario.senha, request.form["senha"]):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
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

# =========================
# LOGIN CLIENTE
# =========================
@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "GET":
        session.pop("cliente_id", None)

    if request.method == "POST":
        telefone = re.sub(r"\D", "", request.form["telefone"])
        senha = request.form["senha"]

        cliente = Cliente.query.filter_by(telefone=telefone).first()
        if cliente and cliente.check_senha(senha):
            session["cliente_id"] = cliente.id
            session["cliente_nome"] = cliente.nome
            return redirect(url_for("cliente_dashboard"))

        flash("Telefone ou senha inválidos")

    return render_template("cliente_login.html")


@app.route("/cliente")
@login_cliente_obrigatorio
def cliente_dashboard():
    return render_template("cliente_dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)