import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

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

def buscar_tesouro():
    url = "https://ghostnetrn.github.io"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = 'utf-8'
        if res.status_code != 200 or "<!DOCTYPE html>" in res.text: return []
        linhas = res.text.strip().split('\n')
        return [{"titulo": c[0].strip(), "taxa": c[1].strip(), "preco": c[2].strip(), "vencimento": c[3].strip()} 
                for l in linhas if len(c := l.split(';')) >= 4 and "Título" not in l]
    except: return []

def buscar_dolar():
    # Usando AwesomeAPI: mais estável e pega a última cotação automaticamente
    try:
        res = requests.get("https://economia.awesomeapi.com.br")
        dados = res.json()['USDBRL']
        return {"valor": f"R$ {float(dados['bid']):.4f}", "data": dados['create_date']}
    except:
        return {"valor": "Indisponível", "data": "--"}

@app.route('/')
def index():
    dados_t = buscar_tesouro()
    dados_d = buscar_dolar()
    linhas_t = "".join([f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>" for t in dados_t])
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Painel de Cotações</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('dolar')">Dólar Hoje</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Sem dados</td></tr>'}</tbody>
                </table>
            </div>
            <div id="dolar" class="content">
                <div class="ptax-box">
                    <h3>Dólar Comercial (Fechamento)</h3>
                    <div class="ptax-valor">{dados_d['valor']}</div>
                    <p>Cotação atualizada em tempo real.</p>
                    <small>Ref: {dados_d['data']}</small>
                </div>
            </div>
        </div>
        <script>
            function switchTab(id) {{
                document.querySelectorAll('.content').forEach(c => c.style.display = 'none');
                document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
                document.getElementById(id).style.display = 'block';
                event.currentTarget.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run()
