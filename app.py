import os
import io
import re
import base64
from datetime import datetime, date
from functools import wraps
from collections import defaultdict
from sqlalchemy import func, desc
from flask import session, request, redirect, render_template, flash, url_for
from sqlalchemy import func

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

PIX_CHAVE = "35548112899"
PIX_NOME = "BRUNA RAFAELA SOARES SILVA"
PIX_CIDADE = "CAIEIRAS"

uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///erp_cayube.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
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
    tipo = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    origem = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.utcnow)


class MovimentoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
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


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), default="geral")
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo


def formatar_valor_pix(valor):
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
    tamanho = str(len(valor)).zfill(2)
    return f"{id_campo}{tamanho}{valor}"


def gerar_payload_pix(chave, nome, cidade, valor, identificador="***"):
    gui = campo_pix("00", "br.gov.bcb.pix")
    chave_pix = campo_pix("01", chave)
    merchant_account = campo_pix("26", gui + chave_pix)

    payload = ""
    payload += campo_pix("00", "01")
    payload += campo_pix("26", merchant_account)
    payload += campo_pix("52", "0000")
    payload += campo_pix("53", "986")
    payload += campo_pix("54", formatar_valor_pix(valor))
    payload += campo_pix("58", "BR")
    payload += campo_pix("59", nome[:25])
    payload += campo_pix("60", cidade[:15])
    payload += campo_pix("62", campo_pix("05", identificador[:25]))
    payload += "6304"

    codigo_crc = crc16(payload)
    return payload + codigo_crc


def gerar_qrcode_base64(texto):
    qr = qrcode.make(texto)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


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
const CACHE_NAME = "cayube-cliente-v1";
const URLS_TO_CACHE = ["/cliente/login", "/cliente", "/static/logo.png"];

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


@app.route("/criar_tabelas")
def criar_tabelas():
    db.create_all()
    return "Tabelas criadas com sucesso!"


@app.route("/atualizar_banco")
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
            conn.commit()
        return "Banco atualizado com sucesso!"
    except Exception as e:
        return f"Erro ao atualizar banco: {str(e)}"


@app.route("/resetar_senha_clientes")
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
                status_pedido="aprovado",
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
        produtos=Produto.query.all(),
        clientes=Cliente.query.all(),
    )


@app.route("/fiado")
@login_obrigatorio
def fiado():
    busca = (request.args.get("busca") or "").strip()

    query = (
        db.session.query(Cliente)
        .join(Venda, Venda.cliente_id == Cliente.id)
        .filter(Venda.pago == False, Venda.forma_pagamento == "fiado")
    )

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(termo),
                Cliente.telefone.ilike(termo),
                Cliente.local.ilike(termo),
            )
        )

    clientes_fiado = query.distinct().order_by(Cliente.nome.asc()).all()

    for cliente in clientes_fiado:
        vendas_abertas = (
            Venda.query.filter(
                Venda.cliente_id == cliente.id,
                Venda.pago == False,
                Venda.forma_pagamento == "fiado",
            )
            .order_by(Venda.data.desc(), Venda.id.desc())
            .all()
        )
        total_divida = sum((v.total or 0) for v in vendas_abertas)
        cliente.divida = total_divida
        cliente.vendas_abertas = vendas_abertas

    total_fiado = sum((cliente.divida or 0) for cliente in clientes_fiado)
    quantidade_clientes = len(clientes_fiado)

    return render_template(
        "fiado.html",
        clientes_fiado=clientes_fiado,
        busca=busca,
        total_fiado=total_fiado,
        quantidade_clientes=quantidade_clientes,
    )


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
@login_obrigatorio
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


@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        telefone_input = re.sub(r"\D", "", request.form.get("telefone", ""))
        senha = request.form.get("senha", "").strip()

        # pega TODOS os clientes
        clientes = Cliente.query.all()

        cliente_encontrado = None

        for c in clientes:
            tel = re.sub(r"\D", "", c.telefone or "")

            # comparação flexível
            if tel == telefone_input or tel.endswith(telefone_input[-8:]):
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

        # LOGIN OK
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
    clientes = Cliente.query.all()
    produtos = Produto.query.filter(Produto.estoque > 0).all()

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
                    pago=(forma != "fiado")
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
    produtos = Produto.query.all()

    if request.method == "POST":
        tipo = request.form.get("tipo")

        # 🔹 PRODUTO NORMAL
        if tipo == "produto":
            produto_id = int(request.form.get("produto_id"))
            quantidade = int(request.form.get("quantidade"))
            valor = float(request.form.get("valor"))

            produto = Produto.query.get(produto_id)
            saldo = get_saldo()

            if produto:
                produto.estoque += quantidade
                saldo.conta -= valor

                db.session.add(MovimentoEstoque(
                    produto_id=produto.id,
                    tipo="entrada",
                    quantidade=quantidade,
                    motivo="Entrada rápida"
                ))

        # 🔹 ENTRADA DIVERSA
        elif tipo == "diverso":
            valor = float(request.form.get("valor_diverso"))
            saldo = get_saldo()

            saldo.conta -= valor

        db.session.commit()
        flash("Entrada registrada com sucesso!", "success")
        return redirect(url_for("entrada_rapida"))

    return render_template("entrada_rapida.html", produtos=produtos)

@app.route("/cliente")
def cliente_dashboard():
    if "cliente_id" not in session:
        return redirect(url_for("login_cliente"))

    cliente_id = session["cliente_id"]
    cliente = Cliente.query.get_or_404(cliente_id)

    # TODOS os pedidos do cliente
    pedidos = Pedido.query.filter_by(
        cliente_id=cliente_id
    ).order_by(Pedido.id.desc()).all()

    # FILTROS
    pedidos_abertos = [
        p for p in pedidos
        if (p.status or "").lower() in ["aberto", "pendente", "fiado"]
    ]

    historico = [
        p for p in pedidos
        if (p.status or "").lower() in ["entregue", "finalizado", "pago", "concluido"]
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
                forma_pagamento="pix",
                data=datetime.utcnow(),
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


@app.route("/pedidos_clientes")
@login_obrigatorio
def pedidos_clientes():
    pedidos = (
        db.session.query(Venda, Cliente, Produto)
        .join(Cliente, Venda.cliente_id == Cliente.id)
        .join(Produto, Venda.produto_id == Produto.id)
        .order_by(Venda.data.desc())
        .all()
    )

    return render_template("pedidos_clientes.html", pedidos=pedidos)


@app.route("/aprovar_pedido/<int:venda_id>")
@login_obrigatorio
def aprovar_pedido(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    produto = Produto.query.get(venda.produto_id)

    if venda.status_pedido != "aguardando_aprovacao":
        flash("Esse pedido já foi analisado.", "warning")
        return redirect(url_for("pedidos_clientes"))

    if not produto or produto.estoque < venda.quantidade:
        flash("Estoque insuficiente para aprovar o pedido.", "danger")
        return redirect(url_for("pedidos_clientes"))

    venda.status_pedido = "aprovado"
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
@login_obrigatorio
def resetar_banco():
    db.drop_all()
    db.create_all()
    return "Banco resetado com sucesso!"


@app.route("/notificacoes")
@login_obrigatorio
def notificacoes():
    itens = Notificacao.query.order_by(Notificacao.lida.asc(), Notificacao.data.desc()).all()
    return render_template("notificacoes.html", notificacoes=itens)


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
                "data": n.data.strftime("%d/%m/%Y %H:%M") if n.data else ""
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