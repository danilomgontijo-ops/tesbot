import os
import requests
from flask import Flask, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# HTML com Tabela de Rolagem para o Histórico
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor Financeiro 2026</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f7f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1000px; margin: auto; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #1a73e8; }
        .tabs { display: flex; border-bottom: 2px solid #ddd; margin-bottom: 20px; justify-content: center; }
        .tab-btn { padding: 12px 25px; cursor: pointer; border: none; background: none; font-size: 16px; font-weight: bold; color: #666; }
        .tab-btn.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; }
        .content { display: none; }
        .content.active { display: block; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid #eee; position: sticky; top: 0; }
        td { padding: 12px; border-bottom: 1px solid #eee; }
        .scroll-area { max-height: 500px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; }
        .price { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Painel Financeiro 2026</h1>
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('tesouro')">Tesouro Direto</button>
            <button class="tab-btn" onclick="showTab('dolar')">Dólar (Últimos 12 Meses)</button>
        </div>

        <div id="tesouro" class="content active">
            <div class="scroll-area">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>
                        {% for t in tesouro %}
                        <tr><td>{{ t.titulo }}</td><td>{{ t.vencimento }}</td><td>{{ t.taxa }}</td><td class="price">{{ t.preco }}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="dolar" class="content">
            <div class="scroll-area">
                <table>
                    <thead><tr><th>Data</th><th>Compra (R$)</th><th>Venda (R$)</th></tr></thead>
                    <tbody>
                        {% for d in dolar %}
                        <tr>
                            <td>{{ d.data }}</td>
                            <td>{{ d.compra }}</td>
                            <td>{{ d.venda }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function showTab(id) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

def fetch_tesouro():
    url = "https://raw.githubusercontent.com"
    try:
        r = requests.get(url, timeout=10)
        r.encoding = 'utf-8'
        linhas = r.text.strip().split('\n')
        resultado = []
        for l in linhas:
            p = [col.strip() for col in l.split(';')]
            if len(p) >= 4 and "Título" not in l:
                resultado.append({"titulo": p[0], "taxa": p[1], "preco": p[2], "vencimento": p[3]})
        return resultado
    except: return []

def fetch_dolar_historico():
    # Endpoint da AwesomeAPI para os últimos 365 dias (12 meses)
    url = "https://economia.awesomeapi.com.br"
    try:
        r = requests.get(url, timeout=15)
        dados = r.json()
        historico = []
        for d in dados:
            dt = datetime.fromtimestamp(int(d['timestamp'])).strftime('%d/%m/%Y')
            historico.append({
                "data": dt,
                "compra": f"{float(d['bid']):.4f}",
                "venda": f"{float(d['ask']):.4f}"
            })
        return historico
    except: return []

@app.route('/')
def index():
    t_data = fetch_tesouro()
    d_data = fetch_dolar_historico()
    return render_template_string(HTML_TEMPLATE, tesouro=t_data, dolar=d_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
