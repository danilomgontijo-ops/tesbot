import requests
from flask import Flask, render_template_string, request
from flask_cors import CORS
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO
import re
import os  # Added for port handling

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
    th { background: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #eee; position: sticky; top: 0; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .preco { color: #188038; font-weight: bold; }
    .scroll-table { max-height: 500px; overflow-y: auto; border: 1px solid #eee; margin-top: 20px; border-radius: 8px; }
    form { margin-top: 20px; }
    input { margin: 5px; padding: 5px; }
    .resultado { margin-top: 20px; font-weight: bold; color: #1a73e8; }
</style>
"""

def buscar_tesouro():
    url = "https://raw.githubusercontent.com/ghostnetrn/bot-tesouro-direto/refs/heads/main/rendimento_resgatar.csv"
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200: return []
        linhas = res.text.strip().split('\n')
        return [{"titulo": c[0].strip(), "vencimento": c[3].strip(), "taxa": c[1].strip(), "preco": c[2].strip()} 
                for l in linhas if len(c := l.split(';')) >= 4 and "Título" not in l]
    except: return []

def buscar_historico_dolar():
    try:
        data_final = datetime.now().strftime('%m-%d-%Y')
        data_inicial = (datetime.now() - timedelta(days=360)).strftime('%m-%d-%Y')
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{data_inicial}'&@dataFinalCotacao='{data_final}'&$top=360&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao&$orderby=dataHoraCotacao desc"
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.json()['value']
        return []
    except: return []

def mapear_titulo_para_codigo(titulo):
    titulo_lower = titulo.lower()
    ano = re.search(r'\d{4}', titulo).group(0) if re.search(r'\d{4}', titulo) else None
    if not ano:
        return None, None
    if 'selic' in titulo_lower:
        codigo = 'LFT'
    elif 'prefixado com juros semestrais' in titulo_lower:
        codigo = 'NTN-F'
    elif 'prefixado' in titulo_lower:
        codigo = 'LTN'
    elif 'ipca+ com juros semestrais' in titulo_lower:
        codigo = 'NTN-B'
    elif 'ipca+' in titulo_lower:
        codigo = 'NTN-B Principal'
    elif 'igpm+' in titulo_lower:
        codigo = 'NTN-C'
    else:
        return None, None
    return codigo, ano

def buscar_historico_titulo(codigo, ano):
    try:
        file_name = f"{codigo.replace(' ', '_')}_{ano}.xls"
        url = f"https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/sistd/{ano}/{file_name}"
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return None
        wb = openpyxl.load_workbook(filename=BytesIO(res.content))
        sheet = wb.active
        data = {}
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0]:
                data_dt = row[0] if isinstance(row[0], datetime) else datetime.strptime(row[0], '%d/%m/%Y')
                data_str = data_dt.strftime('%d/%m/%Y')
                data[data_str] = {
                    'preco_compra': float(row[2].replace(',', '.')) if isinstance(row[2], str) else float(row[2]),
                    'preco_venda': float(row[4].replace(',', '.')) if isinstance(row[4], str) else float(row[4])
                }
        return data
    except:
        return None

def encontrar_preco_mais_proximo(historico, data_str, tipo_preco, anterior=True):
    data_alvo = datetime.strptime(data_str, '%d/%m/%Y')
    datas = sorted([datetime.strptime(d, '%d/%m/%Y') for d in historico.keys()])
    if data_alvo.strftime('%d/%m/%Y') in historico:
        return historico[data_alvo.strftime('%d/%m/%Y')][tipo_preco]
    if anterior:
        for d in reversed(datas):
            if d <= data_alvo:
                return historico[d.strftime('%d/%m/%Y')][tipo_preco]
    return None

@app.route('/')
def index():
    dados_t = buscar_tesouro()
    dados_d = buscar_historico_dolar()
    
    linhas_t = "".join([f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>" for t in dados_t])
    
    linhas_d = ""
    for d in dados_d:
        data_br = datetime.strptime(d['dataHoraCotacao'], '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y')
        linhas_d += f"<tr><td>{data_br}</td><td>R$ {d['cotacaoCompra']:.4f}</td><td>R$ {d['cotacaoVenda']:.4f}</td></tr>"

    titulos_options = "".join([f"<option value='{t['titulo']}'>{t['titulo']}</option>" for t in dados_t])

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Dashboard Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Cotações e Histórico</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('ptax')">Dólar (Últimos 12 Meses)</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Dados do Tesouro indisponíveis no momento.</td></tr>'}</tbody>
                </table>
                <form action="/calcular_rendimento" method="get">
                    <label>Calcular Rendimento:</label><br>
                    <select name="titulo">{titulos_options}</select>
                    <input type="text" name="data_inicio" placeholder="Data Início (DD/MM/AAAA)">
                    <input type="text" name="data_fim" placeholder="Data Fim (DD/MM/AAAA)">
                    <button type="submit">Calcular</button>
                </form>
            </div>
            <div id="ptax" class="content">
                <div class="scroll-table">
                    <table>
                        <thead><tr><th>Data</th><th>Compra</th><th>Venda</th></tr></thead>
                        <tbody>{linhas_d or '<tr><td colspan="3">Dados do Dólar indisponíveis no momento.</td></tr>'}</tbody>
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

@app.route('/calcular_rendimento')
def calcular_rendimento():
    titulo = request.args.get('titulo')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not all([titulo, data_inicio, data_fim]):
        return "Parâmetros incompletos."

    codigo, ano = mapear_titulo_para_codigo(titulo)
    if not codigo:
        return "Título não reconhecido ou sem ano de vencimento."

    historico = buscar_historico_titulo(codigo, ano)
    if not historico:
        return "Dados históricos indisponíveis para este título."

    preco_compra = encontrar_preco_mais_proximo(historico, data_inicio, 'preco_compra')
    preco_venda = encontrar_preco_mais_proximo(historico, data_fim, 'preco_venda')

    if preco_compra is None or preco_venda is None:
        return "Datas não encontradas nos históricos (verifique dias úteis)."

    rendimento = (preco_venda / preco_compra - 1) * 100
    nota_cupom = " (Nota: Ignora cupons intermediários se o título tiver juros semestrais)." if 'juros semestrais' in titulo.lower() else ""

    return f"Rendimento de {titulo} de {data_inicio} a {data_fim}: {rendimento:.2f}%{nota_cupom}"

if __name__ == '__main__':
    import os
    # O Fly e o Koyeb usam a porta da variável de ambiente PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
