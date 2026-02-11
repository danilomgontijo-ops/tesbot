import os
import requests
from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Estilo visual simplificado para evitar erros de renderização
ESTILO_CSS = """
<style>
    body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
    .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #1a73e8; text-align: center; }
    .nav { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
    button { padding: 10px; cursor: pointer; border: 1px solid #ddd; background: #eee; border-radius: 5px; }
    button.active { background: #1a73e8; color: white; border-color: #1a73e8; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
    .preco { color: green; font-weight: bold; }
    .content { display: none; }
    .active-content { display: block; }
</style>
"""

def get_tesouro():
    url = "https://raw.githubusercontent.com"
    try:
        r = requests.get(url, timeout=10)
        r.encoding = 'utf-8'
        if r.status_code != 200: return []
        linhas = r.text.strip().split('\n')
        dados = []
        for l in linhas:
            c = [col.strip() for col in l.split(';')]
            if len(c) >= 4 and "Título" not in l:
                dados.append({"t": c[0], "v": c[1], "tx": c[2], "p": c[3]})
        return dados
    except: return []

def get_dolar():
    try:
        r = requests.get("https://economia.awesomeapi.com.br", timeout=10)
        d = r.json()['USDBRL']
        return {"venda": d['ask'], "data": d['create_date']}
    except: return None

@app.route('/')
def home():
    t_dados = get_tesouro()
    d_dados = get_dolar()
    
    linhas_t = "".join([f"<tr><td>{x['t']}</td><td>{x['v']}</td><td>{x['tx']}</td><td class='preco'>{x['p']}</td></tr>" for x in t_dados])
    
    dolar_html = f"<h3>Dólar Comercial: R$ {float(d_dados['venda']):.4f}</h3><p>Atualizado em: {d_dados['data']}</p>" if d_dados else "Dólar indisponível"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Cotações Financeiras</h1>
            <div class="nav">
                <button onclick="tab('t')" id="bt">Tesouro</button>
                <button onclick="tab('d')" id="bd">Dólar</button>
            </div>
            <div id="t" class="content active-content">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Erro ao carregar dados.</td></tr>'}</tbody>
                </table>
            </div>
            <div id="d" class="content">
                <div style="text-align:center; padding: 30px; background: #f9f9f9; border-radius: 10px;">
                    {dolar_html}
                </div>
            </div>
        </div>
        <script>
            function tab(id) {{
                document.getElementById('t').style.display = id === 't' ? 'block' : 'none';
                document.getElementById('d').style.display = id === 'd' ? 'block' : 'none';
                document.getElementById('bt').className = id === 't' ? 'active' : '';
                document.getElementById('bd').className = id === 'd' ? 'active' : '';
            }}
            tab('t');
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    # Configuração vital para evitar Erro de Porta no Fly/Koyeb/Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
