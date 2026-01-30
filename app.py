import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

ESTILO_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
    .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    h1 { color: #1a73e8; text-align: center; }
    .nav-tabs { display: flex; justify-content: center; margin-bottom: 20px; border-bottom: 2px solid #eee; }
    .tab-button { padding: 10px 20px; cursor: pointer; border: none; background: none; font-size: 1.1em; color: #5f6368; border-bottom: 3px solid transparent; }
    .tab-button.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; font-weight: bold; }
    .content { display: none; }
    .content.active { display: block; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { background: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid #eee; }
    td { padding: 12px; border-bottom: 1px solid #eee; font-size: 0.9em; }
    .preco { color: #188038; font-weight: bold; }
    .ptax-box { text-align: center; padding: 50px; background: #f8f9fa; border-radius: 8px; border: 1px solid #eee; }
    .ptax-valor { font-size: 3.5em; color: #1a73e8; font-weight: bold; margin: 10px 0; }
</style>
"""

def buscar_tesouro_csv():
    url = "https://ghostnetrn.github.io/bot-tesouro-direto/rendimento_resgatar.csv"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code != 200 or "<!DOCTYPE html>" in response.text:
            return []
        linhas = response.text.strip().split('\n')
        dados = []
        for linha in linhas:
            cols = [c.strip() for c in linha.split(';')]
            if len(cols) >= 4 and "Título" not in cols[0]:
                dados.append({
                    "titulo": cols[0],
                    "taxa": cols[1],
                    "preco": cols[2],
                    "vencimento": cols[3]
                })
        return dados
    except:
        return []

def buscar_ptax():
    hoje = datetime.now().strftime('%m-%d-%Y')
    url = f"https://olinda.bcb.gov.br'{hoje}'&$format=json"
    try:
        res = requests.get(url).json()
        if not res['value']:
            ontem = (datetime.now() - timedelta(1)).strftime('%m-%d-%Y')
            url = f"https://olinda.bcb.gov.br'{ontem}'&$format=json"
            res = requests.get(url).json()
        item = res['value'][0]
        return {"valor": f"R$ {item['cotacaoVenda']:.4f}", "data": item['dataHoraCotacao']}
    except:
        return {"valor": "Consultando...", "data": "Aguarde"}

@app.route('/')
def index():
    dados_t = buscar_tesouro_csv()
    dados_d = buscar_ptax()
    linhas_html = ""
    for t in dados_t:
        linhas_html += f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>"
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Painel de Cotações</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('dolar')">Dólar PTAX</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_html if dados_t else '<tr><td colspan="4">Carregando dados...</td></tr>'}</tbody>
                </table>
            </div>
            <div id="dolar" class="content">
                <div class="ptax-box">
                    <h3>Dólar PTAX (Banco Central)</h3>
                    <div class="ptax-valor">{dados_d['valor']}</div>
                    <p>Fonte Oficial: Banco Central do Brasil</p>
                    <small>Ref: {dados_d['data']}</small>
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
    app.run()
