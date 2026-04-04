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

# ========================
# BANCO DE DADOS
# ========================
uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    uri = "sqlite:///erp_cayube.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ========================
# MANIFEST ERP
# ========================
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

# ========================
# MANIFEST CLIENTE
# ========================
@app.route("/manifest-cliente.webmanifest")
def manifest_cliente():
    return jsonify({
        "id": "/cliente/login",
        "name": "Cayube Área do Cliente",
        "short_name": "Cliente Cayube",
        "start_url": "/cliente/login",
        "scope": "/cliente",
        "display": "standalone",
        "background_color": "#f4f6f9",
        "theme_color": "#1e1e2f",
        "icons": [
            {"src": "/static/icons/cliente-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/cliente-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })

# ========================
# SERVICE WORKER ERP
# ========================
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

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

# ========================
# SERVICE WORKER CLIENTE
# ========================
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

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
"""
    return app.response_class(js, mimetype="application/javascript")

# ========================
# LOGIN ADMIN
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["usuario"] == "admin" and request.form["senha"] == "123":
            session["usuario"] = "admin"
            return redirect(url_for("index"))
        flash("Login inválido")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# ========================
# LOGIN CLIENTE
# ========================
@app.route("/cliente/login", methods=["GET", "POST"])
def login_cliente():
    if request.method == "POST":
        session["cliente"] = request.form["telefone"]
        return redirect(url_for("cliente_dashboard"))
    return render_template("cliente_login.html")

@app.route("/cliente/logout")
def cliente_logout():
    session.pop("cliente", None)
    return redirect(url_for("login_cliente"))

@app.route("/cliente")
def cliente_dashboard():
    if "cliente" not in session:
        return redirect(url_for("login_cliente"))
    return render_template("cliente_dashboard.html")

# ========================
# RODAR
# ========================
if __name__ == "__main__":
    app.run(debug=True)