import os
import requests
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Design moderno e limpo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Financeiro 2026</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #eef2f7; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1000px; margin: auto; background: #fff; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #1a73e8; margin-bottom: 25px; }
        .tabs { display: flex; border-bottom: 2px solid #ddd; margin-bottom: 20px; }
        .tab-btn { padding: 12px 25px; cursor: pointer; border: none; background: none; font-size: 16px; font-weight: 600; color: #666; transition: 0.3s; }
        .tab-btn.active { color: #1a73e8; border-bottom: 3px solid #1a73e8; }
        .content { display: none; }
        .content.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background: #f8f9fa; color: #555; padding: 15px; text-align: left; border-bottom: 2px solid #eee; }
        td { padding: 15px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f1f8ff; }
        .price { color: #27ae60; font-weight: bold; }
        .dolar-card { text-align: center; padding: 50px; background: #f0f7ff; border-radius: 12px; }
        .dolar-val { font-size: 48px; font-weight: bold; color: #1a73e8; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Monitor Financeiro</h1>
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('tesouro')">Tesouro Direto</button>
            <button class="tab-btn" onclick="showTab('dolar')">Dólar Hoje</button>
        </div>

        <div id="tesouro" class="content active">
            <table>
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Vencimento</th>
                        <th>Taxa Anual</th>
                        <th>Preço Resgate</th>
                    </tr>
                </thead>
                <tbody>
                    {% for t in tesouro %}
                    <tr>
                        <td>{{ t.titulo }}</td>
                        <td>{{ t.vencimento }}</td>
                        <td>{{ t.taxa }}</td>
                        <td class="price">{{ t.preco }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" style="text-align:center;">Nenhum dado encontrado no momento.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div id="dolar" class="content">
            <div class="dolar-card">
                <h3>Cotação Dólar Comercial (USD/BRL)</h3>
                <div class="dolar-val">R$ {{ dolar }}</div>
                <p>Atualizado em: {{ data_dolar }}</p>
                <small>Fonte: AwesomeAPI / Banco Central</small>
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
        if r.status_code != 200: return []
        linhas = r.text.strip().split('\n')
        resultado = []
        for l in linhas:
            partes = [p.strip() for p in l.split(';')]
            if len(partes) >= 4 and "Título" not in l:
                resultado.append({
                    "titulo": partes[0],
                    "taxa": partes[1],
                    "preco": partes[2],
                    "vencimento": partes[3]
                })
        return resultado
    except:
        return []

def fetch_dolar():
    try:
        # Usando AwesomeAPI que é a mais estável para servidores Cloud
        r = requests.get("https://economia.awesomeapi.com.br", timeout=10)
        data = r.json()['USDBRL']
        return f"{float(data['ask']):.4f}", data['create_date']
    except:
        return "Indisponível", "--"

@app.route('/')
def index():
    t_data = fetch_tesouro()
    d_val, d_date = fetch_dolar()
    return render_template_string(HTML_TEMPLATE, tesouro=t_data, dolar=d_val, data_dolar=d_date)

if __name__ == '__main__':
    # Configuração de porta automática para Render, Fly.io e Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
