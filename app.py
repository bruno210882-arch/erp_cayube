
from flask import Flask, render_template
from sqlalchemy import func, desc

app = Flask(__name__)

# --- ROTAS FINANCEIRAS ---

@app.route("/painel_financeiro")
def painel_financeiro():
    return render_template("painel_financeiro.html")

@app.route("/ranking_clientes")
def ranking_clientes():
    return render_template("ranking_clientes.html")

@app.route("/relatorio_fiado_cliente")
def relatorio_fiado_cliente():
    return render_template("relatorio_fiado_cliente.html")

@app.route("/relatorio_fiado_local")
def relatorio_fiado_local():
    return render_template("relatorio_fiado_local.html")
