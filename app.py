import os
import requests
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

# HTML e CSS integrados para carregar tudo de uma vez
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel Financeiro 2026</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .tabs { display: flex; border-bottom: 2px solid #eee; margin-bottom: 20px; }
        .tab-btn { padding: 15px; cursor: pointer; border: none; background: none; font-weight: bold; color: #666; }
        .tab-btn.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; }
        .content { display: none; }
        .active { display: block; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; position: sticky; top: 0; }
        td { padding: 12px; border-bottom: 1px solid #eee; }
        .scroll { max-height: 500px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; }
        .verde { color: #2e7d32; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard Financeiro</h1>
        <div class="tabs">
            <button class="tab-btn active" onclick="tab('t')">Tesouro Direto</button>
            <button class="tab-btn" onclick="tab('d')">Dólar (12 Meses)</button>
        </div>

        <div id="t" class="content active">
            <div class="scroll">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço</th></tr></thead>
                    <tbody>
                        {% for i in tesouro %}
                        <tr><td>{{ i.titulo }}</td><td>{{ i.vencimento }}</td><td>{{ i.taxa }}</td><td class="verde">{{ i.preco }}</td></tr>
                        {% else %}
                        <tr><td colspan="4">Buscando dados no Tesouro...</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="d" class="content">
            <div class="scroll">
                <table>
                    <thead><tr><th>Data</th><th>Compra (R$)</th><th>Venda (R$)</th></tr></thead>
                    <tbody>
                        {% for j in dolar %}
                        <tr><td>{{ j.data }}</td><td>{{ j.compra }}</td><td>{{ j.venda }}</td></tr>
                        {% else %}
                        <tr><td colspan="3">Buscando histórico do Dólar...</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        function tab(id) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

def carregar_tesouro():
    # Usando o JSON oficial do robô (muito mais estável que o CSV)
    url = "https://raw.githubusercontent.com"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            dados = r.json()
            return [{"titulo": x['titulo'], "vencimento": x['vencimento'], "taxa": x['taxa_rendimento'], "preco": x['preco_resgate']} for x in dados]
        return []
    except:
        return []

def carregar_dolar():
    # Histórico de 365 dias (12 meses) via AwesomeAPI
    url = "https://economia.awesomeapi.com.br"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return [{"data": datetime.fromtimestamp(int(d['timestamp'])).strftime('%d/%m/%Y'), 
                     "compra": f"{float(d['bid']):.4f}", 
                     "venda": f"{float(d['ask']):.4f}"} for d in r.json()]
        return []
    except:
        return []

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, tesouro=carregar_tesouro(), dolar=carregar_dolar())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
