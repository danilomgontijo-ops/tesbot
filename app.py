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

def buscar_historico_ptax():
    hoje = datetime.now()
    inicio = hoje - timedelta(days=365)
    data_inicio = inicio.strftime('%m-%d-%Y')
    data_fim = hoje.strftime('%m-%d-%Y')
    
    url = (f"https://olinda.bcb.gov.br"
           f"(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
           f"@dataInicial='{data_inicio}'&@dataFinalCotacao='{data_fim}'&$format=json&$orderby=dataHoraCotacao desc")
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.json().get('value', [])
        return []
    except:
        return []

@app.route('/')
def index():
    dados_t = buscar_tesouro()
    dados_p = buscar_historico_ptax()
    
    linhas_t = ""
    for t in dados_t:
        linhas_t += f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>"
    
    linhas_p = ""
    for p in dados_p:
        data_iso = p['dataHoraCotacao'][:10]
        data_br = datetime.strptime(data_iso, '%Y-%m-%d').strftime('%d/%m/%Y')
        linhas_p += f"<tr><td>{data_br}</td><td>R$ {p['cotacaoCompra']:.4f}</td><td>R$ {p['cotacaoVenda']:.4f}</td></tr>"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Cotações e Histórico</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('ptax')">Histórico PTAX (12 Meses)</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Dados do Tesouro indisponíveis.</td></tr>'}</tbody>
                </table>
            </div>
            <div id="ptax" class="content">
                <div class="scroll-table">
                    <table>
                        <thead><tr><th>Data</th><th>Compra</th><th>Venda</th></tr></thead>
                        <tbody>{linhas_p or '<tr><td colspan="3">Dados do Banco Central indisponíveis.</td></tr>'}</tbody>
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
    """)

if __name__ == '__main__':
    # Esta parte é crucial para Fly.io e Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
