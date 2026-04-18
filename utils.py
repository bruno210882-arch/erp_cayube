from functools import wraps

from flask import redirect, url_for, session, flash

from database import db
from models import Saldo

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


def get_saldo():
    saldo = Saldo.query.first()
    if not saldo:
        saldo = Saldo(dinheiro=0, conta=0)
        db.session.add(saldo)
        db.session.commit()
    return saldo



def serializar_produtos_venda(produtos):
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "preco": float(p.preco or 0),
            "estoque": int(p.estoque or 0),
        }
        for p in produtos
    ]

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
