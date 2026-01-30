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

def buscar_tesouro_csv():
    # URL que você confirmou como correta
    url = "https://ghostnetrn.github.io"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        # Bloqueia se o GitHub retornar HTML de erro em vez de texto
        if response.status_code != 200 or "<!DOCTYPE html>" in response.text:
            return []

        linhas = response.text.strip().split('\n')
        dados = []
        for linha in linhas:
            cols = [c.strip() for c in linha.split(';')]
            # Filtra linhas válidas e pula o cabeçalho
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

@app.route('/')
def index():
    dados_t = buscar_tesouro_csv()
    # Monta as linhas da tabela do Tesouro
    linhas_html = "".join([f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>" for t in dados_t])
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Dashboard Financeiro</title>{ESTILO_CSS}</head>
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
                    <tbody>{linhas_html if dados_t else '<tr><td colspan="4">Carregando dados do Tesouro...</td></tr>'}</tbody>
                </table>
            </div>

            <div id="dolar" class="content">
                <div class="ptax-box">
                    <h3>Dólar PTAX (Venda)</h3>
                    <div class="ptax-valor" id="ptax-valor">Carregando...</div>
                    <p>Fonte Oficial: Banco Central do Brasil</p>
                    <small id="ptax-data">Buscando última cotação disponível...</small>
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

            async function getPtax() {{
                const elValor = document.getElementById('ptax-valor');
                const elData = document.getElementById('ptax-data');
                
                const formatarData = (date) => {{
                    let d = new Date(date),
                        month = '' + (d.getMonth() + 1),
                        day = '' + d.getDate(),
                        year = d.getFullYear();
                    if (month.length < 2) month = '0' + month;
                    if (day.length < 2) day = '0' + day;
                    return [month, day, year].join('-');
                }};

                let dataAlvo = new Date();
                let tentativas = 0;
                let sucesso = false;

                while (tentativas < 5 && !sucesso) {{
                    const dataStr = formatarData(dataAlvo);
                    const url = `https://olinda.bcb.gov.br{{dataStr}}'&$format=json`;
                    
                    try {{
                        const response = await fetch(url);
                        if (!response.ok) throw new Error();
                        const res = await response.json();
                        
                        if (res.value && res.value.length > 0) {{
                            const item = res.value[res.value.length - 1];
                            elValor.innerText = "R$ " + item.cotacaoVenda.toLocaleString('pt-BR', {{minimumFractionDigits: 4}});
                            elData.innerText = "Cotação oficial de: " + item.dataHoraCotacao;
                            sucesso = true;
                        }} else {{
                            dataAlvo.setDate(dataAlvo.getDate() - 1);
                            tentativas++;
                        }}
                    }} catch (e) {{
                        dataAlvo.setDate(dataAlvo.getDate() - 1);
                        tentativas++;
                    }}
                }}
                if (!sucesso) elValor.innerText = "Indisponível no momento";
            }}
            getPtax();
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run()
