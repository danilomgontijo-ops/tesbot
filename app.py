import requests
import os
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

ESTILO_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
    .container { max-width: 1100px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    h1 { color: #1a73e8; text-align: center; }
    .nav-tabs { display: flex; justify-content: center; margin-bottom: 20px; border-bottom: 2px solid #eee; }
    .tab-button { padding: 10px 20px; cursor: pointer; border: none; background: none; font-size: 1.1em; color: #5f6368; border-bottom: 3px solid transparent; }
    .tab-button.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; font-weight: bold; }
    .content { display: none; }
    .content.active { display: block; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9em; }
    th { background: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #eee; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .preco { color: #188038; font-weight: bold; }
    .scroll-table { max-height: 500px; overflow-y: auto; border: 1px solid #eee; margin-top: 20px; border-radius: 8px; }
</style>
"""

def buscar_tesouro():
    url = "https://raw.githubusercontent.com/ghostnetrn/bot-tesouro-direto/refs/heads/main/rendimento_resgatar.csv"
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200: return []
        linhas = res.text.strip().split('\n')
        dados = []
        for l in linhas:
            c = [col.strip() for col in l.split(';')]
            if len(c) >= 4 and "Título" not in c:
                dados.append({"titulo": c[0], "vencimento": c[1], "taxa": c[2], "preco": c[3]})
        return dados
    except: return []

def buscar_dolar_hoje():
    # Usando AwesomeAPI para evitar bloqueio de servidor
    try:
        res = requests.get("https://economia.awesomeapi.com.br", timeout=10)
        if res.status_code == 200:
            dados = res.json()['USDBRL']
            return [{"data": dados['create_date'], "compra": dados['bid'], "venda": dados['ask']}]
        return []
    except: return []

@app.route('/')
def index():
    dados_t = buscar_tesouro()
    dados_d = buscar_dolar_hoje()
    
    linhas_t = "".join([f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>" for t in dados_t])
    
    linhas_d = ""
    for d in dados_d:
        linhas_d += f"<tr><td>{d['data']}</td><td>R$ {float(d['compra']):.4f}</td><td>R$ {float(d['venda']):.4f}</td></tr>"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Cotações Financeiras</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('dolar')">Dólar Comercial</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Dados do Tesouro indisponíveis.</td></tr>'}</tbody>
                </table>
            </div>
            <div id="dolar" class="content">
                <div class="scroll-table">
                    <table>
                        <thead><tr><th>Data/Hora Atualização</th><th>Compra</th><th>Venda</th></tr></thead>
                        <tbody>{linhas_d or '<tr><td colspan="3">Dados do Dólar indisponíveis.</td></tr>'}</tbody>
                    </table>
                </div>
            </div>
        </div>
        <script>
            function switchTab(id) {{
                document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
                document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
                document.getElementById(id).classList.add('active');
                event.currentTarget.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """))

if __name__ == '__main__':
    # Esta parte é crucial para Fly.io e Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
