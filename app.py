import os
import io
import re
import base64
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from functools import wraps
from collections import defaultdict
from sqlalchemy import func, desc
from flask import session, request, redirect, render_template, flash, url_for
from sqlalchemy import func
from datetime import datetime
from zoneinfo import ZoneInfo

def agora_brasil():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

import qrcode
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-change-this-secret")

PIX_CHAVE = "35548112899"
PIX_NOME = "BRUNA RAFAELA SOARES SILVA"
PIX_CIDADE = "CAIEIRAS"

uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///instance/erp_cayube.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0") == "1"

db = SQLAlchemy(app)


def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        if session.get("usuario_nivel") != "admin":
            flash("Acesso restrito ao administrador.", "danger")
            return redirect(url_for("index"))
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
    trocar_senha_primeiro_acesso = db.Column(db.Boolean, default=True)

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
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=True)
    quantidade = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Boolean, default=False)
    forma_pagamento = db.Column(db.String(20))
    data = db.Column(db.DateTime, default=agora_brasil)
    status_pedido = db.Column(db.String(30), default="aguardando_aprovacao")
    status_pix = db.Column(db.String(30), default="pendente")


class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dinheiro = db.Column(db.Float, default=0)
    conta = db.Column(db.Float, default=0)


class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    origem = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=agora_brasil)


class MovimentoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=True)
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=agora_brasil)


class FechamentoCaixa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    saldo_inicial = db.Column(db.Float, default=0)
    entradas = db.Column(db.Float, default=0)
    saidas = db.Column(db.Float, default=0)
    saldo_final = db.Column(db.Float, default=0)
    observacao = db.Column(db.String(200))


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), default="geral")
    mensagem = db.Column(db.String(255), nullable=False)
    venda_id = db.Column(db.Integer, nullable=True)
    lida = db.Column(db.Boolean, default=False)
    data = db.Column(db.DateTime, default=agora_brasil)


with app.app_context():
    db.create_all()


def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo


def normalizar_pix_texto(texto, limite):
    texto = (texto or "").strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    texto = re.sub(r"[^A-Z0-9 /.-]", "", texto)
    return texto[:limite]


def formatar_valor_pix(valor):
    valor = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{valor:.2f}"


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
    valor = str(valor)
    tamanho = str(len(valor.encode("utf-8"))).zfill(2)
    return f"{id_campo}{tamanho}{valor}"


def gerar_payload_pix(chave, nome, cidade, valor, identificador="***"):
    chave = (chave or "").strip()

    nome = normalizar_pix_texto(nome, 25)
    cidade = normalizar_pix_texto(cidade, 15)

    identificador = (identificador or "***").strip().upper()
    identificador = re.sub(r"[^A-Z0-9*.-]", "", identificador)[:25]
    if not identificador:
        identificador = "***"

    gui = campo_pix("00", "br.gov.bcb.pix")
    chave_pix = campo_pix("01", chave)
    merchant_account = campo_pix("26", gui + chave_pix)

    payload = ""
    payload += campo_pix("00", "01")
    payload += merchant_account
    payload += campo_pix("52", "0000")
    payload += campo_pix("53", "986")
    payload += campo_pix("54", formatar_valor_pix(valor))
    payload += campo_pix("58", "BR")
    payload += campo_pix("59", nome)
    payload += campo_pix("60", cidade)
    payload += campo_pix("62", campo_pix("05", identificador))
    payload += "6304"

    return payload + crc16(payload)


def gerar_qrcode_base64(texto):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def gerar_pdf_relatorio_cliente(cliente, vendas, data_inicial="", data_final=""):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    logo_path = os.path.join(app.root_path, "static", "logo.png")
    data_geracao = agora_brasil().strftime("%d/%m/%Y %H:%M") if "agora_brasil" in globals() else datetime.now().strftime("%d/%m/%Y %H:%M")

    def rodape():
        pdf.setFont("Helvetica", 9)
        pdf.setFillColorRGB(0.35, 0.35, 0.35)
        pdf.line(18 * mm, 22 * mm, largura - 18 * mm, 22 * mm)
        pdf.drawString(18 * mm, 16 * mm, f"PIX: {PIX_CHAVE}")
        pdf.drawString(18 * mm, 11 * mm, f"Recebedor: {PIX_NOME} - {PIX_CIDADE}")
        pdf.drawRightString(largura - 18 * mm, 16 * mm, f"Gerado em: {data_geracao}")
        pdf.drawRightString(largura - 18 * mm, 11 * mm, f"Pagina {pdf.getPageNumber()}")

    def desenhar_tabela_header(y):
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColorRGB(0.10, 0.10, 0.10)
        pdf.drawString(18 * mm, y, "Data")
        pdf.drawString(46 * mm, y, "Item")
        pdf.drawString(116 * mm, y, "Forma")
        pdf.drawRightString(150 * mm, y, "Qtd")
        pdf.drawString(156 * mm, y, "Status")
        pdf.drawRightString(192 * mm, y, "Valor")
        y -= 5 * mm
        pdf.line(18 * mm, y, 192 * mm, y)
        return y - 6 * mm

    def cabecalho(y_top):
        if os.path.exists(logo_path):
            try:
                pdf.drawImage(ImageReader(logo_path), 18 * mm, y_top - 14 * mm, width=18 * mm, height=18 * mm, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        pdf.setFillColorRGB(0.08, 0.13, 0.25)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40 * mm, y_top, "ERP Cayube")
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(40 * mm, y_top - 7 * mm, "Relatorio de Valores em Aberto por Cliente")
        pdf.setFont("Helvetica", 10)
        pdf.setFillColorRGB(0.25, 0.25, 0.25)
        pdf.drawString(18 * mm, y_top - 24 * mm, f"Cliente: {cliente.nome}")
        pdf.drawString(18 * mm, y_top - 29 * mm, f"Local: {cliente.local or '-'}")
        periodo = f"Periodo: {data_inicial or 'inicio'} a {data_final or 'hoje'}"
        pdf.drawString(18 * mm, y_top - 34 * mm, periodo)
        pdf.drawRightString(largura - 18 * mm, y_top - 24 * mm, f"Gerado em: {data_geracao}")
        return y_top - 42 * mm

    y = cabecalho(280 * mm)
    total = 0
    y = desenhar_tabela_header(y)

    pdf.setFont("Helvetica", 10)
    for venda, produto in vendas:
        if y < 38 * mm:
            rodape()
            pdf.showPage()
            y = cabecalho(280 * mm)
            y = desenhar_tabela_header(y)
            pdf.setFont("Helvetica", 10)

        nome_produto = produto.nome if produto else "Item diverso"
        data_str = venda.data.strftime("%d/%m/%Y %H:%M") if venda.data else ""
        forma = (venda.forma_pagamento or "-").capitalize()
        status = "Pendente" if not venda.pago else "Pago"
        valor = float(venda.total or 0)

        pdf.drawString(18 * mm, y, data_str[:16])
        pdf.drawString(46 * mm, y, nome_produto[:34])
        pdf.drawString(116 * mm, y, forma)
        pdf.drawRightString(150 * mm, y, str(venda.quantidade or 0))
        pdf.drawString(156 * mm, y, status)
        pdf.drawRightString(192 * mm, y, f"R$ {valor:.2f}")
        total += valor
        y -= 6 * mm

    y -= 2 * mm
    pdf.line(18 * mm, y, 192 * mm, y)
    y -= 8 * mm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(192 * mm, y, f"Total em aberto: R$ {total:.2f}")

    rodape()
    pdf.save()
    buffer.seek(0)
    return buffer


@app.route("/manifest-erp.webmanifest")
def manifest_erp():
    return jsonify({
        "id": "/admin",
        "name": "Cayube ERP Gerencial",
        "short_name": "ERP Cayube",
        "description": "ERP gerencial instalável",
        "start_url": "/login",
        "scope": "/login",
        "display": "standalone",
        "background_color": "#f4f6f9",
        "theme_color": "#1e1e2f",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icons/erp-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/erp-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })



@app.route("/relatorios")
@login_obrigatorio
def relatorios():
    return redirect(url_for("relatorios_gerais"))


@app.route("/relatorios_gerais")
@login_obrigatorio
def relatorios_gerais():
    return render_template("relatorios_gerais.html")

@app.route("/relatorio_vendas_local_data", methods=["GET"])
@login_obrigatorio
def relatorio_vendas_local_data():
    data_inicial = (request.args.get("data_inicial") or "").strip()
    data_final = (request.args.get("data_final") or "").strip()
    local = (request.args.get("local") or "").strip()

    query = (
        db.session.query(
            Cliente.local.label("local"),
            func.date(Venda.data).label("dia"),
            func.count(Venda.id).label("qtd_vendas"),
            func.sum(Venda.quantidade).label("qtd_itens"),
            func.sum(Venda.total).label("total_vendido")
        )
        .join(Cliente, Venda.cliente_id == Cliente.id)
    )

    if data_inicial:
        query = query.filter(func.date(Venda.data) >= data_inicial)
    if data_final:
        query = query.filter(func.date(Venda.data) <= data_final)
    if local:
        query = query.filter(Cliente.local == local)

    resultados = (
        query.group_by(Cliente.local, func.date(Venda.data))
        .order_by(func.date(Venda.data).desc(), Cliente.local.asc())
        .all()
    )

    locais = [l[0] for l in db.session.query(Cliente.local).filter(Cliente.local.isnot(None)).distinct().order_by(Cliente.local.asc()).all()]

    total_geral = sum((r.total_vendido or 0) for r in resultados)

    return render_template(
        "relatorio_vendas_local_data.html",
        resultados=resultados,
        locais=locais,
        filtros={
            "data_inicial": data_inicial,
            "data_final": data_final,
            "local": local
        },
        total_geral=total_geral
    )

@app.route("/cliente/confirmar_pix/<int:venda_id>", methods=["POST"])
@login_cliente_obrigatorio
def cliente_confirmar_pix(venda_id):
    venda = Venda.query.get_or_404(venda_id)

    if venda.cliente_id != session.get("cliente_id"):
        flash("Acesso inválido.", "danger")
        return redirect(url_for("cliente_itens_em_aberto"))

    if venda.pago:
        flash("Essa venda já está paga.", "warning")
        return redirect(url_for("cliente_itens_em_aberto"))

    cliente = Cliente.query.get(venda.cliente_id) if venda.cliente_id else None
    venda.status_pix = "aguardando_confirmacao"
    nome_cliente = cliente.nome if cliente else "Cliente"

    db.session.add(Notificacao(
        tipo="pix",
        mensagem=f"{nome_cliente} informou pagamento de R$ {venda.total}",
        venda_id=venda.id
    ))

    db.session.commit()

    flash("Pagamento enviado para conferência!", "success")
    return redirect(url_for("cliente_itens_em_aberto"))

@app.route("/relatorio_produto_local_dia", methods=["GET"])
@login_obrigatorio
def relatorio_produto_local_dia():
    data_inicial = (request.args.get("data_inicial") or "").strip()
    data_final = (request.args.get("data_final") or "").strip()
    local = (request.args.get("local") or "").strip()
    produto_id = (request.args.get("produto_id") or "").strip()

    query = (
        db.session.query(
            Produto.nome.label("produto"),
            Cliente.local.label("local"),
            func.date(Venda.data).label("dia"),
            func.sum(Venda.quantidade).label("qtd_itens"),
            func.sum(Venda.total).label("total_vendido")
        )
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .join(Produto, Venda.produto_id == Produto.id)
    )

    if data_inicial:
        query = query.filter(func.date(Venda.data) >= data_inicial)
    if data_final:
        query = query.filter(func.date(Venda.data) <= data_final)
    if local:
        query = query.filter(Cliente.local == local)
    if produto_id:
        query = query.filter(Venda.produto_id == int(produto_id))

    resultados = (
        query.group_by(Produto.nome, Cliente.local, func.date(Venda.data))
        .order_by(func.date(Venda.data).desc(), Cliente.local.asc(), Produto.nome.asc())
        .all()
    )

    locais = [l[0] for l in db.session.query(Cliente.local).filter(Cliente.local.isnot(None)).distinct().order_by(Cliente.local.asc()).all()]
    produtos = Produto.query.order_by(Produto.nome.asc()).all()

    total_geral = sum((r.total_vendido or 0) for r in resultados)

    return render_template(
        "relatorio_produto_local_dia.html",
        resultados=resultados,
        locais=locais,
        produtos=produtos,
        filtros={
            "data_inicial": data_inicial,
            "data_final": data_final,
            "local": local,
            "produto_id": produto_id
        },
        total_geral=total_geral
    )



@app.route("/relatorio_cliente_pdf")
@login_obrigatorio
def relatorio_cliente_pdf():
    cliente_id = (request.args.get("cliente_id") or "").strip()
    data_inicial = (request.args.get("data_inicial") or "").strip()
    data_final = (request.args.get("data_final") or "").strip()

    clientes = (
        db.session.query(Cliente)
        .join(Venda, Venda.cliente_id == Cliente.id)
        .filter(Venda.pago == False)
        .distinct()
        .order_by(Cliente.nome.asc())
        .all()
    )
    vendas = []
    cliente = None
    total_cliente = 0

    if cliente_id:
        cliente = Cliente.query.get_or_404(int(cliente_id))
        query = (
            db.session.query(Venda, Produto)
            .outerjoin(Produto, Venda.produto_id == Produto.id)
            .filter(
                Venda.cliente_id == cliente.id,
                Venda.pago == False
            )
        )
        if data_inicial:
            query = query.filter(func.date(Venda.data) >= data_inicial)
        if data_final:
            query = query.filter(func.date(Venda.data) <= data_final)
        vendas = query.order_by(Venda.data.desc(), Venda.id.desc()).all()
        total_cliente = sum(float(v.total or 0) for v, _ in vendas)

        if request.args.get("formato") == "pdf":
            pdf_buffer = gerar_pdf_relatorio_cliente(cliente, vendas, data_inicial, data_final)
            nome_arquivo = f"relatorio_cliente_aberto_{cliente.id}.pdf"
            return send_file(pdf_buffer, as_attachment=True, download_name=nome_arquivo, mimetype="application/pdf")

    return render_template(
        "relatorio_cliente_pdf.html",
        clientes=clientes,
        cliente=cliente,
        vendas=vendas,
        total_cliente=total_cliente,
        filtros={
            "cliente_id": cliente_id,
            "data_inicial": data_inicial,
            "data_final": data_final,
        },
        pix_chave=PIX_CHAVE,
        pix_nome=PIX_NOME,
        pix_cidade=PIX_CIDADE,
    )


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
            {"src": "/static/icons/cliente-erp-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/cliente-erp-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })


@app.route("/service-worker.js")
def service_worker():
    js = """
const CACHE_NAME = "cayube-pwa-v1";
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


@app.route("/cliente-sw.js")
def cliente_service_worker():
    js = """
const CACHE_NAME = "cayube-cliente-v2";
const URLS_TO_CACHE = ["/cliente/login", "/static/logo.png"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(URLS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  if (url.pathname.startsWith("/cliente")) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match("/cliente/login"))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

@app.route("/criar_tabelas")
@admin_obrigatorio
def criar_tabelas():
    db.create_all()
    return "Tabelas criadas com sucesso!"


@app.route("/atualizar_banco")
@admin_obrigatorio
def atualizar_banco():
    try:
        db.create_all()
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE cliente ADD COLUMN IF NOT EXISTS senha_hash VARCHAR(255)"))
            conn.execute(text("ALTER TABLE cliente ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE"))
            conn.execute(text("ALTER TABLE cliente ADD COLUMN IF NOT EXISTS trocar_senha_primeiro_acesso BOOLEAN DEFAULT TRUE"))
            conn.execute(text("UPDATE cliente SET ativo = TRUE WHERE ativo IS NULL OR ativo = FALSE"))
            conn.execute(text("UPDATE cliente SET trocar_senha_primeiro_acesso = TRUE WHERE trocar_senha_primeiro_acesso IS NULL"))
            conn.execute(text("ALTER TABLE venda ADD COLUMN IF NOT EXISTS data TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            conn.execute(text("ALTER TABLE venda ADD COLUMN IF NOT EXISTS status_pedido VARCHAR(30) DEFAULT 'aguardando_aprovacao'"))
            conn.execute(text("ALTER TABLE venda ADD COLUMN IF NOT EXISTS status_pix VARCHAR(30) DEFAULT 'pendente'"))
            conn.execute(text("ALTER TABLE notificacao ADD COLUMN IF NOT EXISTS venda_id INTEGER"))
            conn.commit()
        return "Banco atualizado com sucesso!"
    except Exception as e:
        return f"Erro ao atualizar banco: {str(e)}"


@app.route("/resetar_senha_clientes")
@admin_obrigatorio
def resetar_senha_clientes():
    clientes = Cliente.query.all()
    for c in clientes:
        c.telefone = re.sub(r"\D", "", c.telefone or "")
        c.ativo = True
        c.set_senha("123456")
        c.trocar_senha_primeiro_acesso = True
    db.session.commit()
    return "Senhas resetadas para 123456 e primeiro acesso habilitado."


@app.route("/ativar_clientes")
@admin_obrigatorio
def ativar_clientes():
    clientes = Cliente.query.all()
    for c in clientes:
        c.telefone = re.sub(r"\D", "", c.telefone or "")
        c.ativo = True
        if not c.senha_hash:
            c.set_senha("123456")
        c.trocar_senha_primeiro_acesso = True
    db.session.commit()
    return "Todos os clientes foram ativados com sucesso!"


@app.route("/corrigir_telefones_clientes")
@admin_obrigatorio
def corrigir_telefones_clientes():
    clientes = Cliente.query.all()
    alterados = 0

    for c in clientes:
        telefone_original = c.telefone or ""
        telefone_limpo = re.sub(r"\D", "", telefone_original)
        if telefone_original != telefone_limpo:
            c.telefone = telefone_limpo
            alterados += 1

    db.session.commit()
    return f"Telefones corrigidos com sucesso! {alterados} cadastro(s) atualizados."


@app.route("/debug_clientes")
@admin_obrigatorio
def debug_clientes():
    dados = []
    for c in Cliente.query.order_by(Cliente.id.asc()).all():
        telefone_limpo = re.sub(r"\D", "", c.telefone or "")
        dados.append({
            "id": c.id,
            "nome": c.nome,
            "telefone": c.telefone,
            "telefone_limpo": telefone_limpo,
            "final_8": telefone_limpo[-8:] if telefone_limpo else "",
            "ativo": bool(getattr(c, "ativo", False)),
            "tem_senha": bool(getattr(c, "senha_hash", None)),
            "primeiro_acesso": bool(getattr(c, "trocar_senha_primeiro_acesso", False)),
        })
    return jsonify({"clientes": dados, "total": len(dados)})


@app.route("/criar_admin")
def criar_admin():
    total_usuarios = Usuario.query.count()
    if total_usuarios > 0 and session.get("usuario_nivel") != "admin":
        return "Acesso negado", 403

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
    return "Admin criado com sucesso! Usuario: admin | Senha: 123456"


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


from datetime import date
from sqlalchemy import func

@app.route("/")
@login_obrigatorio
def index():
    hoje = date.today()

    vendas_hoje = db.session.query(func.sum(Venda.total)).filter(
        func.date(Venda.data) == hoje
    ).scalar() or 0

    total_vendas = db.session.query(func.sum(Venda.total)).scalar() or 0

    total_fiado = db.session.query(func.sum(Venda.total)).filter(
        Venda.pago == False
    ).scalar() or 0

    saldo = get_saldo()
    caixa_total = (saldo.dinheiro or 0) + (saldo.conta or 0)

    # top devedores
    top_devedores = db.session.query(
        Cliente.nome,
        func.sum(Venda.total)
    ).join(Venda).filter(
        Venda.pago == False
    ).group_by(Cliente.nome).order_by(
        func.sum(Venda.total).desc()
    ).limit(5).all()

    # dívidas antigas
    antigos = Venda.query.filter(
        Venda.pago == False
    ).order_by(Venda.data.asc()).limit(5).all()

    # estoque baixo
    estoque_baixo = Produto.query.filter(Produto.estoque < 5).all()

    return render_template(
        "index.html",
        vendas_hoje=vendas_hoje,
        total_vendas=total_vendas,
        total_fiado=total_fiado,
        caixa_total=caixa_total,
        top_devedores=top_devedores,
        antigos=antigos,
        estoque_baixo=estoque_baixo
    )

@app.route("/clientes")
@login_obrigatorio
def clientes():
    lista = Cliente.query.all()
    return render_template("clientes.html", clientes=lista)


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
@login_obrigatorio
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        try:
            nome = request.form["nome"].strip()
            telefone = re.sub(r"\D", "", request.form.get("telefone", ""))
            telefone = telefone if telefone else None
            local = request.form.get("local", "").strip()

            if telefone:
                existe = Cliente.query.filter(
                    Cliente.telefone == telefone,
                    Cliente.id != cliente.id
                ).first()

                if existe:
                    flash("Já existe outro cliente com esse telefone.", "danger")
                    return redirect(url_for("editar_cliente", id=cliente.id))

            cliente.nome = nome
            cliente.telefone = telefone
            cliente.local = local

            db.session.commit()
            flash("Cliente atualizado com sucesso.", "success")
            return redirect(url_for("clientes"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao editar cliente: {str(e)}"

    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/add_cliente", methods=["POST"])
@login_obrigatorio
def add_cliente():
    try:
        nome = request.form["nome"].strip()
        telefone = re.sub(r"\D", "", request.form.get("telefone", ""))
        telefone = telefone if telefone else None
        local = request.form.get("local", "").strip()

        if telefone:
            existe = Cliente.query.filter_by(telefone=telefone).first()
            if existe:
                flash("Já existe cliente com esse telefone.", "danger")
                return redirect(url_for("clientes"))

        novo = Cliente(
            nome=nome,
            telefone=telefone,
            local=local,
            ativo=True,
            trocar_senha_primeiro_acesso=True,
        )
        novo.set_senha("123456")

        db.session.add(novo)
        db.session.commit()

        flash("Cliente cadastrado com sucesso! Senha padrão: 123456", "success")
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
        cliente.ativo = True
        cliente.trocar_senha_primeiro_acesso = True
        db.session.commit()
        flash("Senha definida com sucesso.", "success")
        return redirect(url_for("clientes"))

    return render_template("definir_senha_cliente.html", cliente=cliente)


@app.route("/confirmar_pix_divida/<int:cliente_id>")
@login_obrigatorio
def confirmar_pix_divida(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    saldo = get_saldo()

    valor_aberto = cliente.divida or 0
    if valor_aberto <= 0:
        flash("Esse cliente não possui valores em aberto.", "warning")
        return redirect(url_for("clientes"))

    saldo.conta += valor_aberto
    cliente.divida = 0

    vendas_abertas = Venda.query.filter_by(
        cliente_id=cliente.id,
        pago=False,
        forma_pagamento="fiado"
    ).all()

    for venda in vendas_abertas:
        venda.pago = True
        venda.status_pix = "pago"
        venda.forma_pagamento = "pix"

    movimento = Movimento(
        tipo="entrada",
        valor=valor_aberto,
        origem="conta",
        descricao=f"Recebimento PIX de valores em aberto - Cliente: {cliente.nome}"
    )

    db.session.add(movimento)
    db.session.commit()

    flash("PIX dos valores em aberto confirmado com sucesso.", "success")
    return redirect(url_for("clientes"))


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
                forma_pagamento=forma,
                status_pedido="venda_direta",
                status_pix="pago" if forma == "pix" else ("pendente" if forma == "fiado" else "pago")
            )

            produto.estoque -= quantidade

            mov_estoque = MovimentoEstoque(
                produto_id=produto_id,
                tipo="saida",
                quantidade=quantidade,
                motivo="Venda administrativa"
            )

            db.session.add(nova_venda)
            db.session.add(mov_estoque)

            if pago:
                if forma == "dinheiro":
                    saldo.dinheiro += total
                else:
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
        produtos=Produto.query.order_by(Produto.nome.asc()).all(),
        clientes=Cliente.query.order_by(Cliente.nome.asc()).all(),
    )

@app.route("/fiado")
@login_obrigatorio
def fiado():
    busca = (request.args.get("busca") or "").strip()

    query = (
        db.session.query(Venda, Cliente, Produto)
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.pago == False, Venda.forma_pagamento == "fiado")
    )

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(termo),
                Cliente.telefone.ilike(termo),
                Cliente.local.ilike(termo),
                Produto.nome.ilike(termo),
            )
        )

    vendas_fiado = query.order_by(Cliente.nome.asc(), Venda.data.desc(), Venda.id.desc()).all()

    resumo_query = (
        db.session.query(
            Cliente.id,
            Cliente.nome,
            Cliente.local,
            func.sum(Venda.total).label("total_divida"),
            func.count(Venda.id).label("qtd_lancamentos")
        )
        .join(Venda, Venda.cliente_id == Cliente.id)
        .filter(Venda.pago == False, Venda.forma_pagamento == "fiado")
    )

    if busca:
        termo = f"%{busca}%"
        resumo_query = resumo_query.filter(
            db.or_(
                Cliente.nome.ilike(termo),
                Cliente.telefone.ilike(termo),
                Cliente.local.ilike(termo),
            )
        )

    clientes_resumo = (
        resumo_query
        .group_by(Cliente.id, Cliente.nome, Cliente.local)
        .order_by(func.sum(Venda.total).desc())
        .all()
    )

    total_geral_fiado = sum(c.total_divida or 0 for c in clientes_resumo)
    total_clientes = len(clientes_resumo)
    total_lancamentos = len(vendas_fiado)

    return render_template(
        "fiado.html",
        vendas_fiado=vendas_fiado,
        clientes_resumo=clientes_resumo,
        total_geral_fiado=total_geral_fiado,
        total_clientes=total_clientes,
        total_lancamentos=total_lancamentos,
        busca=busca
    )

@app.route("/quitar_fiado_cliente/<int:cliente_id>", methods=["POST"])
@login_obrigatorio
def quitar_fiado_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    saldo = get_saldo()
    forma = (request.form.get("forma") or "").strip().lower()

    if forma not in ["dinheiro", "transferencia"]:
        flash("Escolha Dinheiro ou Transferência.", "warning")
        return redirect(url_for("fiado"))

    vendas_abertas = Venda.query.filter_by(
        cliente_id=cliente.id,
        pago=False,
        forma_pagamento="fiado"
    ).all()

    if not vendas_abertas:
        flash("Esse cliente não possui lançamentos em aberto.", "warning")
        return redirect(url_for("fiado"))

    total_recebido = 0

    for venda in vendas_abertas:
        venda.pago = True
        venda.forma_pagamento = forma
        venda.status_pix = "pago"
        total_recebido += float(venda.total or 0)

    if forma == "dinheiro":
        saldo.dinheiro += total_recebido
    else:
        saldo.conta += total_recebido

    cliente.divida = 0

    db.session.add(Movimento(
        tipo="entrada",
        valor=total_recebido,
        origem="dinheiro" if forma == "dinheiro" else "conta",
        descricao=f"Quitação total do fiado - Cliente: {cliente.nome}"
    ))

    db.session.commit()
    flash("Fiado do cliente quitado com sucesso.", "success")
    return redirect(url_for("fiado"))


@app.route("/receber_venda/<int:venda_id>", methods=["POST"])
@login_obrigatorio
def receber_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    cliente = Cliente.query.get(venda.cliente_id)
    saldo = get_saldo()

    forma = (request.form.get("forma") or "").strip().lower()
    if forma not in ["dinheiro", "transferencia"]:
        flash("Escolha Dinheiro ou Transferência para dar baixa.", "warning")
        return redirect(url_for("fiado"))

    if not venda.pago:
        venda.pago = True
        venda.forma_pagamento = forma
        venda.status_pix = "pago"

        if forma == "dinheiro":
            saldo.dinheiro = (saldo.dinheiro or 0) + (venda.total or 0)
        else:
            saldo.conta = (saldo.conta or 0) + (venda.total or 0)

        if cliente:
            cliente.divida = max((cliente.divida or 0) - (venda.total or 0), 0)

        db.session.commit()
        flash("Baixa realizada com sucesso!", "success")

    return redirect(url_for("fiado"))

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
    return render_template("movimentacao.html", movimentos=movimentos, saldo=saldo)


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




@app.route("/inventario_estoque", methods=["GET"])
@login_obrigatorio
def inventario_estoque():
    busca = (request.args.get("busca") or "").strip()
    somente_baixo = (request.args.get("baixo") or "").strip() == "1"

    query = Produto.query
    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))
    if somente_baixo:
        query = query.filter(Produto.estoque <= 5)

    produtos = query.order_by(Produto.nome.asc()).all()
    total_itens = len(produtos)
    total_unidades = sum((p.estoque or 0) for p in produtos)
    total_custo = sum((p.custo or 0) * (p.estoque or 0) for p in produtos)
    total_venda = sum((p.preco or 0) * (p.estoque or 0) for p in produtos)

    movimentos = (
        MovimentoEstoque.query
        .filter(MovimentoEstoque.motivo.ilike("%inventário%"))
        .order_by(MovimentoEstoque.data.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "inventario_estoque.html",
        produtos=produtos,
        movimentos=movimentos,
        busca=busca,
        somente_baixo=somente_baixo,
        total_itens=total_itens,
        total_unidades=total_unidades,
        total_custo=total_custo,
        total_venda=total_venda,
    )


@app.route("/ajustar_inventario/<int:produto_id>", methods=["POST"])
@login_obrigatorio
def ajustar_inventario(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    try:
        estoque_contado = int(request.form.get("estoque_contado", 0))
        observacao = (request.form.get("observacao") or "").strip()
    except ValueError:
        flash("Informe uma quantidade válida para o inventário.", "danger")
        return redirect(url_for("inventario_estoque"))

    estoque_atual = int(produto.estoque or 0)
    diferenca = estoque_contado - estoque_atual

    if diferenca == 0:
        flash(f"Nenhum ajuste necessário para {produto.nome}.", "info")
        return redirect(url_for("inventario_estoque"))

    produto.estoque = estoque_contado
    movimento = MovimentoEstoque(
        produto_id=produto.id,
        tipo="entrada" if diferenca > 0 else "saida",
        quantidade=abs(diferenca),
        motivo=f"Ajuste de inventário{' - ' + observacao if observacao else ''}",
    )
    db.session.add(movimento)
    db.session.commit()

    flash(f"Inventário ajustado para {produto.nome}. Diferença registrada: {diferenca:+d} unidade(s).", "success")
    return redirect(url_for("inventario_estoque"))

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


@app.route("/relatorio_estoque")
@login_obrigatorio
def relatorio_estoque():
    produtos = Produto.query.all()
    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()
    return render_template("relatorio_estoque.html", produtos=produtos, movimentos=movimentos)


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
        relatorio.append({
            "data": dia,
            "entradas": valores["entradas"],
            "saidas": valores["saidas"],
            "saldo": valores["entradas"] - valores["saidas"]
        })

    relatorio.sort(key=lambda x: x["data"], reverse=True)
    return render_template("fluxo_caixa.html", relatorio=relatorio)


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
                db.session.add(FechamentoCaixa(
                    data=hoje,
                    saldo_inicial=saldo_inicial,
                    entradas=entradas,
                    saidas=saidas,
                    saldo_final=saldo_final,
                    observacao=observacao
                ))

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


@app.route("/usuarios", methods=["GET", "POST"])
@admin_obrigatorio
def usuarios():
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        try:
            novo = Usuario(
                nome=request.form["nome"],
                usuario=request.form["usuario"],
                senha=generate_password_hash(request.form["senha"]),
                nivel=request.form["nivel"]
            )

            db.session.add(novo)
            db.session.commit()
            return redirect(url_for("usuarios"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar usuário: {str(e)}"

    return render_template("usuarios.html", usuarios=Usuario.query.all())


@app.route("/alterar_senha/<int:id>", methods=["POST"])
@admin_obrigatorio
def alterar_senha(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    if usuario:
        usuario.senha = generate_password_hash(request.form["nova_senha"])
        db.session.commit()

    return redirect(url_for("usuarios"))


@app.route("/excluir_usuario/<int:id>")
@admin_obrigatorio
def excluir_usuario(id):
    if session.get("usuario_nivel") != "admin":
        return "Acesso negado"

    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

    return redirect(url_for("usuarios"))


@app.route("/backup")
@admin_obrigatorio
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


@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        telefone_input = re.sub(r"\D", "", request.form.get("telefone", ""))
        senha = request.form.get("senha", "").strip()

        if not telefone_input or not senha:
            flash("Informe telefone e senha.", "danger")
            return render_template("cliente_login.html")

        cliente_encontrado = Cliente.query.filter_by(telefone=telefone_input).first()

        if not cliente_encontrado and len(telefone_input) >= 8:
            clientes = Cliente.query.filter(Cliente.telefone.isnot(None)).all()
            sufixo = telefone_input[-8:]
            for c in clientes:
                tel = re.sub(r"\D", "", c.telefone or "")
                if tel.endswith(sufixo):
                    cliente_encontrado = c
                    break

        if not cliente_encontrado:
            flash("Telefone não encontrado.", "danger")
            return render_template("cliente_login.html")

        if not cliente_encontrado.ativo:
            flash("Cliente inativo.", "danger")
            return render_template("cliente_login.html")

        if not cliente_encontrado.check_senha(senha):
            flash("Senha inválida.", "danger")
            return render_template("cliente_login.html")

        session["cliente_id"] = cliente_encontrado.id
        session["cliente_nome"] = cliente_encontrado.nome

        if cliente_encontrado.trocar_senha_primeiro_acesso:
            return redirect(url_for("cliente_primeira_senha"))

        return redirect(url_for("cliente_dashboard"))

    return render_template("cliente_login.html")

@app.route("/cliente/primeira_senha", methods=["GET", "POST"])
def cliente_primeira_senha():
    if "cliente_id" not in session:
        return redirect(url_for("login_cliente"))

    cliente = Cliente.query.get_or_404(session["cliente_id"])

    if request.method == "POST":
        nova_senha = request.form.get("nova_senha", "").strip()
        confirmar_senha = request.form.get("confirmar_senha", "").strip()

        if len(nova_senha) < 4:
            flash("A nova senha deve ter pelo menos 4 caracteres.", "danger")
            return redirect(url_for("cliente_primeira_senha"))

        if nova_senha != confirmar_senha:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("cliente_primeira_senha"))

        cliente.set_senha(nova_senha)
        cliente.trocar_senha_primeiro_acesso = False
        db.session.commit()

        flash("Senha alterada com sucesso.", "success")
        return redirect(url_for("cliente_dashboard"))

    return render_template("cliente_primeira_senha.html", cliente=cliente)


@app.route("/cliente/logout")
def cliente_logout():
    session.pop("cliente_id", None)
    session.pop("cliente_nome", None)
    flash("Você saiu da área do cliente.", "success")
    return redirect(url_for("login_cliente"))

@app.route("/venda_rapida", methods=["GET", "POST"])
@login_obrigatorio
def venda_rapida():
    clientes = Cliente.query.order_by(Cliente.nome.asc()).all()
    produtos = Produto.query.filter(Produto.estoque > 0).order_by(Produto.nome.asc()).all()

    if "carrinho" not in session:
        session["carrinho"] = []

    if request.method == "POST":
        acao = request.form.get("acao")

        # 🔹 ADICIONAR PRODUTO
        if acao == "add_produto":
            produto_id = int(request.form.get("produto_id"))
            quantidade = int(request.form.get("quantidade", 1))

            produto = Produto.query.get(produto_id)

            if produto and produto.estoque >= quantidade:
                item = {
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "quantidade": quantidade,
                    "preco": float(produto.preco)
                }
                session["carrinho"].append(item)
                session.modified = True
            else:
                flash("Estoque insuficiente.", "danger")

        # 🔹 ITEM DIVERSO
        elif acao == "add_diverso":
            nome = request.form.get("nome_diverso")
            valor = float(request.form.get("valor_diverso"))

            item = {
                "produto_id": None,
                "nome": nome,
                "quantidade": 1,
                "preco": valor
            }

            session["carrinho"].append(item)
            session.modified = True

        # 🔹 REMOVER ITEM
        elif acao == "remover":
            indice = int(request.form.get("indice"))
            if 0 <= indice < len(session["carrinho"]):
                session["carrinho"].pop(indice)
                session.modified = True

        # 🔹 LIMPAR CARRINHO
        elif acao == "limpar":
            session["carrinho"] = []
            session.modified = True

        # 🔹 FINALIZAR VENDA
        elif acao == "finalizar":
            cliente_id = int(request.form.get("cliente_id"))
            forma = request.form.get("forma_pagamento")

            cliente = Cliente.query.get(cliente_id)
            saldo = get_saldo()

            total_geral = 0

            for item in session["carrinho"]:
                total = item["quantidade"] * item["preco"]

                # baixa estoque se for produto real
                if item["produto_id"]:
                    produto = Produto.query.get(item["produto_id"])
                    if produto:
                        produto.estoque -= item["quantidade"]

                venda = Venda(
                    produto_id=item["produto_id"],
                    cliente_id=cliente.id,
                    quantidade=item["quantidade"],
                    total=total,
                    forma_pagamento=forma,
                    pago=(forma != "fiado"),
                    status_pedido="venda_direta",
                    status_pix="pago" if forma in ["dinheiro", "transferencia", "pix"] else "pendente",
                )

                db.session.add(venda)
                total_geral += total

                # financeiro
                if forma == "fiado":
                    cliente.divida = (cliente.divida or 0) + total
                else:
                    if forma == "dinheiro":
                        saldo.dinheiro += total
                    else:
                        saldo.conta += total

            session["carrinho"] = []
            session.modified = True

            db.session.commit()

            flash(f"Venda finalizada! Total: R$ {total_geral:.2f}", "success")
            return redirect(url_for("venda_rapida"))

    total = sum(i["quantidade"] * i["preco"] for i in session["carrinho"])

    return render_template(
        "venda_rapida.html",
        clientes=clientes,
        produtos=produtos,
        carrinho=session["carrinho"],
        total=total
    )

@app.route("/entrada_rapida", methods=["GET", "POST"])
@login_obrigatorio
def entrada_rapida():
    produtos = Produto.query.order_by(Produto.nome.asc()).all()
    saldo = get_saldo()

    if request.method == "POST":
        try:
            produto_id = request.form.get("produto_id")
            quantidade = int(request.form.get("quantidade", 0) or 0)
            valor_compra = float(request.form.get("valor_compra", 0) or 0)
            origem = (request.form.get("origem") or "").strip().lower()

            if not produto_id or quantidade <= 0 or valor_compra < 0:
                flash("Preencha os dados da entrada corretamente.", "warning")
                return redirect(url_for("entrada_rapida"))

            produto = Produto.query.get_or_404(int(produto_id))
            produto.estoque = (produto.estoque or 0) + quantidade

            if origem == "dinheiro":
                saldo.dinheiro = (saldo.dinheiro or 0) - valor_compra
            elif origem == "conta":
                saldo.conta = (saldo.conta or 0) - valor_compra
            elif origem == "capital_dinheiro":
                saldo.dinheiro = (saldo.dinheiro or 0) + valor_compra
            elif origem == "capital_conta":
                saldo.conta = (saldo.conta or 0) + valor_compra

            db.session.add(MovimentoEstoque(
                produto_id=produto.id,
                tipo="entrada",
                quantidade=quantidade,
                motivo="Entrada rápida"
            ))

            db.session.add(Movimento(
                tipo="entrada" if origem.startswith("capital_") else "saida",
                valor=valor_compra,
                origem="dinheiro" if origem in ["dinheiro", "capital_dinheiro"] else "conta",
                descricao=f"Entrada rápida de estoque - {produto.nome}"
            ))

            db.session.commit()
            flash("Entrada registrada com sucesso!", "success")
            return redirect(url_for("entrada_rapida"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao registrar entrada rápida: {str(e)}", "danger")
            return redirect(url_for("entrada_rapida"))

    movimentos = (
        MovimentoEstoque.query
        .filter_by(tipo="entrada")
        .order_by(MovimentoEstoque.data.desc())
        .limit(20)
        .all()
    )

    return render_template("entrada_rapida.html", produtos=produtos, saldo=saldo, movimentos=movimentos)

@app.route("/cliente")
@login_cliente_obrigatorio
def cliente_dashboard():

    cliente_id = session["cliente_id"]
    cliente = Cliente.query.get_or_404(cliente_id)

    pedidos = (
        Venda.query
        .filter_by(cliente_id=cliente_id)
        .order_by(Venda.data.desc(), Venda.id.desc())
        .all()
    )

    pedidos_abertos = [
        p for p in pedidos
        if (not p.pago) and ((p.status_pedido or "").lower() not in ["recusado"])
    ]

    historico = [
        p for p in pedidos
        if p.pago or ((p.status_pedido or "").lower() in ["aprovado", "entregue", "finalizado"])
    ]

    total_aberto = sum(float(p.total or 0) for p in pedidos_abertos)

    return render_template(
        "cliente_dashboard.html",
        cliente=cliente,
        pedidos=pedidos,
        pedidos_abertos=pedidos_abertos,
        historico=historico,
        total_aberto=total_aberto
    )

@app.route("/cliente/estoque")
@login_cliente_obrigatorio
def cliente_estoque():
    produtos = Produto.query.filter(Produto.estoque > 0).order_by(Produto.nome.asc()).all()
    return render_template("cliente_estoque.html", produtos=produtos)


@app.route("/cliente/pedido", methods=["GET", "POST"])
@login_cliente_obrigatorio
def cliente_pedido():
    cliente = Cliente.query.get_or_404(session["cliente_id"])
    produtos = Produto.query.filter(Produto.estoque > 0).order_by(Produto.nome.asc()).all()

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
                forma_pagamento="pix",
                data=agora_brasil(),
                status_pedido="aguardando_aprovacao",
                status_pix="pendente"
            )

            db.session.add(nova)
            db.session.commit()

            flash("Pedido enviado com sucesso. Aguarde aprovação do administrador.", "success")
            return redirect(url_for("cliente_pedido"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar pedido do cliente: {str(e)}"

    pedidos_realizados = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.cliente_id == cliente.id)
        .order_by(Venda.data.desc())
        .all()
    )

    return render_template("cliente_pedido.html", produtos=produtos, pedidos_realizados=pedidos_realizados, cliente=cliente)


@app.route("/cliente/historico")
@login_cliente_obrigatorio
def cliente_historico():
    cliente = Cliente.query.get_or_404(session["cliente_id"])

    pedidos = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(
            Venda.cliente_id == cliente.id,
            db.or_(Venda.pago == True, Venda.status_pedido.in_(["aprovado", "entregue", "finalizado"]))
        )
        .order_by(Venda.data.desc())
        .all()
    )

    return render_template("cliente_historico.html", cliente=cliente, pedidos=pedidos)


@app.route("/cliente/itens_em_aberto")
@login_cliente_obrigatorio
def cliente_itens_em_aberto():
    cliente = Cliente.query.get_or_404(session["cliente_id"])

    itens_abertos = (
        db.session.query(Venda, Produto)
        .join(Produto, Venda.produto_id == Produto.id)
        .filter(
            Venda.cliente_id == cliente.id,
            Venda.pago == False,
            Venda.status_pedido != "recusado"
        )
        .order_by(Venda.data.desc())
        .all()
    )

    total_aberto = sum((venda.total or 0) for venda, _produto in itens_abertos)

    return render_template(
        "cliente_itens_em_aberto.html",
        cliente=cliente,
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

    payload_pix = gerar_payload_pix(
        chave=PIX_CHAVE,
        nome=PIX_NOME,
        cidade=PIX_CIDADE,
        valor=pedido.total,
        identificador=f"PED{pedido.id}"
    )

    qr_code_base64 = gerar_qrcode_base64(payload_pix)

    return render_template(
        "cliente_pix.html",
        cliente=cliente,
        pedido=pedido,
        valor_aberto=pedido.total,
        payload_pix=payload_pix,
        qr_code_base64=qr_code_base64
    )


@app.route("/cliente/pix_divida")
@login_cliente_obrigatorio
def cliente_pix_divida():
    cliente = Cliente.query.get_or_404(session["cliente_id"])
    valor_aberto = cliente.divida or 0

    if valor_aberto <= 0:
        flash("Você não possui valores em aberto.", "warning")
        return redirect(url_for("cliente_dashboard"))

    payload_pix = gerar_payload_pix(
        chave=PIX_CHAVE,
        nome=PIX_NOME,
        cidade=PIX_CIDADE,
        valor=valor_aberto,
        identificador=f"DIV{cliente.id}"
    )

    qr_code_base64 = gerar_qrcode_base64(payload_pix)

    return render_template(
        "cliente_pix_divida.html",
        cliente=cliente,
        valor_aberto=valor_aberto,
        payload_pix=payload_pix,
        qr_code_base64=qr_code_base64
    )


@app.route("/cliente/notificacoes")
@login_cliente_obrigatorio
def cliente_notificacoes():
    itens = Notificacao.query.order_by(
        Notificacao.lida.asc(),
        Notificacao.data.desc()
    ).all()
    return render_template("cliente_notificacoes.html", notificacoes=itens)

@app.route("/notificacoes/marcar_todas")
@login_obrigatorio
def marcar_todas_notificacoes():
    Notificacao.query.filter_by(lida=False).update({"lida": True})
    db.session.commit()
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("notificacoes"))


@app.route("/api/cliente_notificacoes")
@login_cliente_obrigatorio
def api_cliente_notificacoes():
    itens = Notificacao.query.order_by(
        Notificacao.lida.asc(),
        Notificacao.data.desc()
    ).all()

    return jsonify({
        "itens": [
            {
                "id": n.id,
                "tipo": n.tipo or "geral",
                "mensagem": n.mensagem,
                "lida": bool(n.lida),
                "data": n.data.strftime("%d/%m/%Y %H:%M") if n.data else ""
            }
            for n in itens
        ]
    })

@app.route("/validar_pix_cliente/<int:venda_id>")
@login_obrigatorio
def validar_pix_cliente(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    saldo = get_saldo()
    cliente = Cliente.query.get(venda.cliente_id) if venda.cliente_id else None

    if venda.status_pix != "aguardando_confirmacao":
        flash("Esse pagamento não está aguardando confirmação.", "warning")
        return redirect(url_for("notificacoes"))

    venda.status_pix = "pago"
    venda.pago = True
    venda.forma_pagamento = "pix"
    saldo.conta = (saldo.conta or 0) + (venda.total or 0)

    if cliente:
        cliente.divida = max((cliente.divida or 0) - (venda.total or 0), 0)

    notif = Notificacao.query.filter_by(venda_id=venda.id, tipo="pix").order_by(Notificacao.data.desc()).first()
    if notif:
        notif.lida = True
        notif.mensagem = f"Pagamento PIX validado para {cliente.nome if cliente else 'cliente'} - R$ {venda.total}"

    db.session.add(Notificacao(
        tipo="pix",
        mensagem=f"PIX validado e lançado no caixa: R$ {venda.total}",
        venda_id=venda.id
    ))

    db.session.commit()
    flash("Pagamento PIX validado com sucesso.", "success")
    return redirect(url_for("fiado"))

@app.route("/pedidos_clientes")
@login_obrigatorio
def pedidos_clientes():
    pedidos = (
        db.session.query(Venda, Cliente, Produto)
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .outerjoin(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.status_pedido == "aguardando_aprovacao")
        .order_by(Venda.data.desc())
        .all()
    )

    return render_template("pedidos_clientes.html", pedidos=pedidos)

@app.route("/aprovar_pedido/<int:venda_id>", methods=["GET", "POST"])
@login_obrigatorio
def aprovar_pedido(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    produto = Produto.query.get(venda.produto_id)
    cliente = Cliente.query.get(venda.cliente_id) if venda.cliente_id else None
    saldo = get_saldo()

    if venda.status_pedido != "aguardando_aprovacao":
        flash("Esse pedido já foi analisado.", "warning")
        return redirect(url_for("pedidos_clientes"))

    forma_pagamento = (request.form.get("forma_pagamento") or request.args.get("forma_pagamento") or "pix").strip().lower()
    if forma_pagamento not in ["dinheiro", "transferencia", "pix", "fiado"]:
        flash("Escolha uma forma de pagamento válida.", "danger")
        return redirect(url_for("pedidos_clientes"))

    if not produto or produto.estoque < venda.quantidade:
        flash("Estoque insuficiente para aprovar o pedido.", "danger")
        return redirect(url_for("pedidos_clientes"))

    produto.estoque -= venda.quantidade
    venda.status_pedido = "aprovado"
    venda.forma_pagamento = forma_pagamento

    if forma_pagamento == "pix":
        venda.pago = False
        venda.status_pix = "pendente"
    elif forma_pagamento == "fiado":
        venda.pago = False
        venda.status_pix = "pendente"
        if cliente:
            cliente.divida = (cliente.divida or 0) + (venda.total or 0)
    elif forma_pagamento == "dinheiro":
        venda.pago = True
        venda.status_pix = "pago"
        saldo.dinheiro += venda.total or 0
    else:
        venda.pago = True
        venda.status_pix = "pago"
        saldo.conta += venda.total or 0

    db.session.add(MovimentoEstoque(
        produto_id=produto.id,
        tipo="saida",
        quantidade=venda.quantidade,
        motivo=f"Pedido cliente aprovado - {forma_pagamento}"
    ))

    db.session.add(Notificacao(
        tipo="pedido",
        mensagem=f"Pedido de {cliente.nome if cliente else 'cliente'} aprovado como {forma_pagamento}."
    ))

    if produto.estoque is not None and produto.estoque <= 5:
        db.session.add(Notificacao(
            tipo="estoque",
            mensagem=f"Produto {produto.nome} está com estoque baixo: {produto.estoque}"
        ))

    db.session.commit()

    flash("Pedido aprovado com sucesso.", "success")
    return redirect(url_for("pedidos_clientes"))
@app.route("/recusar_pedido/<int:venda_id>")
@login_obrigatorio
def recusar_pedido(venda_id):
    venda = Venda.query.get_or_404(venda_id)

    if venda.status_pedido != "aguardando_aprovacao":
        flash("Esse pedido já foi analisado.", "warning")
        return redirect(url_for("pedidos_clientes"))

    venda.status_pedido = "recusado"
    venda.status_pix = "cancelado"
    db.session.commit()

    flash("Pedido recusado.", "warning")
    return redirect(url_for("pedidos_clientes"))


@app.route("/confirmar_pix/<int:venda_id>")
@login_obrigatorio
def confirmar_pix(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    cliente = Cliente.query.get(venda.cliente_id)
    produto = Produto.query.get(venda.produto_id)
    saldo = get_saldo()

    if venda.status_pedido != "aprovado":
        flash("O pedido precisa ser aprovado antes de confirmar o PIX.", "danger")
        return redirect(url_for("pedidos_clientes"))

    if venda.status_pix == "pago":
        flash("Esse PIX já foi confirmado.", "warning")
        return redirect(url_for("pedidos_clientes"))

    if not produto or produto.estoque < venda.quantidade:
        flash("Estoque insuficiente no momento da confirmação.", "danger")
        return redirect(url_for("pedidos_clientes"))

    venda.status_pix = "pago"
    venda.pago = True
    venda.forma_pagamento = "pix"

    produto.estoque -= venda.quantidade
    saldo.conta += venda.total

    db.session.add(MovimentoEstoque(
        produto_id=produto.id,
        tipo="saida",
        quantidade=venda.quantidade,
        motivo="Pedido cliente aprovado + PIX confirmado"
    ))

    if cliente:
        cliente.divida = max((cliente.divida or 0) - venda.total, 0)

    db.session.commit()

    flash("Recebimento PIX confirmado com sucesso.", "success")
    return redirect(url_for("pedidos_clientes"))


@app.route("/baixa_estoque", methods=["GET", "POST"])
@login_obrigatorio
def baixa_estoque():
    produtos = Produto.query.all()

    if request.method == "POST":
        try:
            produto_id = int(request.form.get("produto_id"))
            quantidade = int(request.form.get("quantidade"))
            motivo = request.form.get("motivo", "").strip()

            produto = Produto.query.get_or_404(produto_id)

            if quantidade <= 0:
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("baixa_estoque"))

            if (produto.estoque or 0) < quantidade:
                flash("Estoque insuficiente para a baixa.", "danger")
                return redirect(url_for("baixa_estoque"))

            produto.estoque -= quantidade

            movimento = MovimentoEstoque(
                produto_id=produto.id,
                tipo="saida",
                quantidade=quantidade,
                motivo=motivo or "Baixa sem venda"
            )

            db.session.add(movimento)
            db.session.commit()

            flash("Baixa de estoque registrada com sucesso.", "success")
            return redirect(url_for("baixa_estoque"))

        except Exception as e:
            db.session.rollback()
            return f"Erro ao registrar baixa de estoque: {str(e)}"

    movimentos = MovimentoEstoque.query.order_by(MovimentoEstoque.data.desc()).all()

    return render_template(
        "baixa_estoque.html",
        produtos=produtos,
        movimentos=movimentos
    )


@app.route("/resetar_banco")
@admin_obrigatorio
def resetar_banco():
    db.drop_all()
    db.create_all()
    return "Banco resetado com sucesso!"


@app.route("/notificacoes")
@login_obrigatorio
def notificacoes():
    itens = Notificacao.query.order_by(Notificacao.lida.asc(), Notificacao.data.desc()).all()
    return render_template("notificacoes.html", notificacoes=itens)


@app.route("/notificacoes/marcar_todas")
@login_obrigatorio
def marcar_todas_notificacoes():
    Notificacao.query.filter_by(lida=False).update({"lida": True})
    db.session.commit()
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("notificacoes"))


@app.route("/api/notificacoes")
@login_obrigatorio
def api_notificacoes():
    itens = Notificacao.query.order_by(Notificacao.lida.asc(), Notificacao.data.desc()).all()
    return jsonify({
        "itens": [
            {
                "id": n.id,
                "tipo": (n.tipo or "geral").capitalize(),
                "mensagem": n.mensagem,
                "lida": bool(n.lida),
                "data": n.data.strftime("%d/%m/%Y %H:%M") if n.data else "",
                "venda_id": n.venda_id
            }
            for n in itens
        ]
    })


@app.route("/api/cliente_notificacoes")
@login_cliente_obrigatorio
def api_cliente_notificacoes():
    itens = Notificacao.query.order_by(Notificacao.lida.asc(), Notificacao.data.desc()).all()
    return jsonify({
        "itens": [
            {
                "id": n.id,
                "tipo": (n.tipo or "geral").capitalize(),
                "mensagem": n.mensagem,
                "lida": bool(n.lida),
                "data": n.data.strftime("%d/%m/%Y %H:%M") if n.data else "",
                "venda_id": n.venda_id
            }
            for n in itens
        ]
    })


@app.route("/notificacao/lida/<int:id>")
@login_obrigatorio
def marcar_lida(id):
    notificacao = Notificacao.query.get_or_404(id)
    notificacao.lida = True
    db.session.commit()
    return redirect(url_for("notificacoes"))

# ===============================
# 💰 PAINEL FINANCEIRO
# ===============================
@app.route("/painel_financeiro")
@login_obrigatorio
def painel_financeiro():
    total_fiado = db.session.query(func.sum(Venda.total)).filter(Venda.pago == False).scalar() or 0

    top_devedores = db.session.query(
        Cliente.nome,
        func.sum(Venda.total).label("total")
    ).join(Venda).filter(
        Venda.pago == False
    ).group_by(Cliente.nome).order_by(desc("total")).limit(5).all()

    antigos = Venda.query.filter(
        Venda.pago == False
    ).order_by(Venda.data.asc()).limit(5).all()

    return render_template(
        "painel_financeiro.html",
        total_fiado=total_fiado,
        top_devedores=top_devedores,
        antigos=antigos
    )


# ===============================
# 🏆 RANKING CLIENTES
# ===============================
@app.route("/ranking_clientes")
@login_obrigatorio
def ranking_clientes():
    ranking = db.session.query(
        Cliente.nome,
        func.sum(Venda.total).label("total")
    ).join(Venda).group_by(Cliente.nome).order_by(desc("total")).limit(10).all()

    return render_template("ranking_clientes.html", ranking=ranking)


# ===============================
# 📊 FIADO POR CLIENTE
# ===============================
@app.route("/relatorio_fiado_cliente")
@login_obrigatorio
def relatorio_fiado_cliente():
    dados = db.session.query(
        Cliente.nome,
        func.sum(Venda.total)
    ).join(Venda).filter(
        Venda.pago == False
    ).group_by(Cliente.nome).all()

    return render_template("relatorio_fiado_cliente.html", dados=dados)


# ===============================
# 📍 FIADO POR LOCAL
# ===============================
@app.route("/relatorio_fiado_local")
@login_obrigatorio
def relatorio_fiado_local():
    dados = db.session.query(
        Cliente.local,
        func.sum(Venda.total)
    ).join(Venda).filter(
        Venda.pago == False
    ).group_by(Cliente.local).all()

    return render_template("relatorio_fiado_local.html", dados=dados)



@app.route("/vendas_diretas")
@login_obrigatorio
def vendas_diretas():
    data_inicial = (request.args.get("data_inicial") or "").strip()
    data_final = (request.args.get("data_final") or "").strip()
    cliente_id = (request.args.get("cliente_id") or "").strip()
    forma = (request.args.get("forma") or "").strip().lower()

    query = (
        db.session.query(Venda, Cliente, Produto)
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .outerjoin(Produto, Venda.produto_id == Produto.id)
        .filter(Venda.status_pedido.in_(["venda_direta", "aprovado"]))
    )

    if data_inicial:
        query = query.filter(func.date(Venda.data) >= data_inicial)
    if data_final:
        query = query.filter(func.date(Venda.data) <= data_final)
    if cliente_id:
        query = query.filter(Venda.cliente_id == int(cliente_id))
    if forma:
        query = query.filter(func.lower(Venda.forma_pagamento) == forma)

    vendas = query.order_by(Venda.data.desc(), Venda.id.desc()).all()

    total_vendas = sum((v.total or 0) for v, _, _ in vendas)
    total_recebido = sum((v.total or 0) for v, _, _ in vendas if v.pago)
    total_pendente = sum((v.total or 0) for v, _, _ in vendas if not v.pago)

    filtros = {
        "data_inicial": data_inicial,
        "data_final": data_final,
        "cliente_id": cliente_id,
        "forma": forma,
    }

    return render_template(
        "vendas_diretas.html",
        vendas=vendas,
        clientes=Cliente.query.order_by(Cliente.nome.asc()).all(),
        filtros=filtros,
        total_vendas=total_vendas,
        total_recebido=total_recebido,
        total_pendente=total_pendente,
    )

@app.route("/excluir_venda/<int:venda_id>")
@login_obrigatorio
def excluir_venda(venda_id):
    return cancelar_venda(venda_id)


@app.route("/cliente/notificacao/lida/<int:id>")
@login_cliente_obrigatorio
def cliente_marcar_lida(id):
    notificacao = Notificacao.query.get_or_404(id)
    notificacao.lida = True
    db.session.commit()
    return redirect(url_for("cliente_dashboard"))


# ===============================
# ❌ CANCELAMENTO DE VENDA
# ===============================
@app.route("/cancelar_venda/<int:id>")
@login_obrigatorio
def cancelar_venda(id):
    venda = Venda.query.get_or_404(id)
    produto = Produto.query.get(venda.produto_id)
    cliente = Cliente.query.get(venda.cliente_id)
    saldo = get_saldo()

    # devolve estoque
    produto.estoque += venda.quantidade

    # ajusta financeiro
    if venda.pago:
        if venda.forma_pagamento == "dinheiro":
            saldo.dinheiro -= venda.total
        else:
            saldo.conta -= venda.total
    else:
        cliente.divida -= venda.total

    db.session.delete(venda)
    db.session.commit()

    flash("Venda cancelada!", "success")
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)
