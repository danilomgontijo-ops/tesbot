import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Estilo CSS para a tabela ficar bonita
ESTILO_CSS = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
    .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #2c3e50; text-align: center; }
    .atualizacao { text-align: center; color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th { background-color: #2980b9; color: white; padding: 12px; text-align: left; }
    td { padding: 12px; border-bottom: 1px solid #ddd; }
    tr:hover { background-color: #f1f1f1; }
    .badge { padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em; }
    .preco { color: #27ae60; font-weight: bold; }
</style>
"""

def buscar_dados():
    url_csv = "https://ghostnetrn.github.io"
    try:
        response = requests.get(url_csv)
        response.encoding = 'utf-8'
        linhas = response.text.strip().split('\n')
        
        titulos = []
        for linha in linhas:
            cols = linha.split(';')
            if len(cols) >= 4:
                titulos.append({
                    "titulo": cols[0].strip(),
                    "taxa": cols[1].strip(),
                    "preco": cols[2].strip(),
                    "vencimento": cols[3].strip()
                })
        return titulos
    except:
        return []

@app.route('/api/precos')
def api_precos():
    dados = buscar_dados()
    return jsonify({"ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "dados": dados})

@app.route('/')
def index():
    dados = buscar_dados()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Monitor Tesouro Direto</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>📊 Preços de Resgate - Tesouro Direto</h1>
            <p class="atualizacao">Última extração realizada em: <strong>{data_hora}</strong></p>
            <table>
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Vencimento</th>
                        <th>Taxa (Anual)</th>
                        <th>Preço de Resgate</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'<tr><td>{t["titulo"]}</td><td>{t["vencimento"]}</td><td><span class="badge" style="background:#e8f4fd; color:#2980b9">{t["taxa"]}</span></td><td class="preco">{t["preco"]}</td></tr>' for t in dados])}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run()
