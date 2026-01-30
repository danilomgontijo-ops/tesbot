import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Layout Profissional
ESTILO_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px; }
    .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    h1 { color: #1a73e8; text-align: center; margin-bottom: 5px; }
    .atualizacao { text-align: center; color: #5f6368; margin-bottom: 30px; font-size: 0.9em; }
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #f8f9fa; color: #3c4043; padding: 15px; text-align: left; border-bottom: 2px solid #eee; }
    td { padding: 15px; border-bottom: 1px solid #eee; font-size: 0.95em; }
    tr:hover { background-color: #f1f3f4; }
    .preco { color: #188038; font-weight: bold; }
    .taxa { background: #e8f0fe; color: #1967d2; padding: 4px 8px; border-radius: 4px; font-weight: 500; }
</style>
"""

def buscar_dados():
    # LINK RAW CORRETO (Este link entrega só o texto do CSV)
    url_csv = "https://ghostnetrn.github.io/bot-tesouro-direto/rendimento_resgatar.csv"
    try:
        response = requests.get(url_csv)
        response.encoding = 'utf-8'
        
        # Se o GitHub retornar erro ou HTML, interrompe
        if response.status_code != 200 or "<!DOCTYPE html>" in response.text:
            return []

        linhas = response.text.strip().split('\n')
        titulos = []
        
        for linha in linhas:
            cols = linha.split(';')
            # Filtra apenas linhas que tenham a estrutura de dados (Título;Taxa;Preço;Vencimento)
            if len(cols) >= 4 and "Título" not in cols[0]:
                titulos.append({
                    "titulo": cols[0].strip(),
                    "taxa": cols[1].strip(),
                    "preco": cols[2].strip(),
                    "vencimento": cols[3].strip()
                })
        return titulos
    except:
        return []

@app.route('/')
def index():
    dados = buscar_dados()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Se não houver dados, mostra aviso
    if not dados:
        corpo_tabela = "<tr><td colspan='4' style='text-align:center'>Aguardando atualização dos dados do GitHub...</td></tr>"
    else:
        corpo_tabela = "".join([f"""
            <tr>
                <td>{t['titulo']}</td>
                <td>{t['vencimento']}</td>
                <td><span class='taxa'>{t['taxa']}</span></td>
                <td class='preco'>{t['preco']}</td>
            </tr>
        """ for t in dados])

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Tesouro Direto</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>📈 Cotações Tesouro Direto</h1>
            <p class="atualizacao">Dados extraídos via API em: <strong>{agora}</strong></p>
            <table>
                <thead>
                    <tr>
                        <th>Título</th>
                        <th>Vencimento</th>
                        <th>Taxa</th>
                        <th>Preço de Resgate</th>
                    </tr>
                </thead>
                <tbody>
                    {corpo_tabela}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """)

@app.route('/api/precos')
def api():
    return jsonify(buscar_dados())

if __name__ == '__main__':
    app.run()
