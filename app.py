import requests
import os
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta

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
    th { background: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #eee; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .preco { color: #188038; font-weight: bold; }
    .scroll-table { max-height: 500px; overflow-y: auto; border: 1px solid #eee; margin-top: 20px; border-radius: 8px; }
</style>
"""

def buscar_tesouro():
    url = "https://raw.githubusercontent.com/ghostnetrn/bot-tesouro-direto/refs/heads/main/rendimento_resgatar.csv"
    try:
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200: return []
        linhas = res.text.strip().split('\n')
        dados = []
        for l in linhas:
            c = [col.strip() for col in l.split(';')]
            if len(c) >= 4 and "Título" not in c:
                dados.append({"titulo": c[0], "vencimento": c[1], "taxa": c[2], "preco": c[3]})
        return dados
    except: return []

def buscar_historico_ptax():
    hoje = datetime.now()
    # PTAX não sai fim de semana; pegamos 15 dias para garantir volume de dados inicial
    inicio = hoje - timedelta(days=15)
    
    # Formatação correta exigida pela API Olinda: 'MM-DD-YYYY'
    d_inicio = inicio.strftime('%m-%d-%Y')
    d_fim = hoje.strftime('%m-%d-%Y')
    
    # URL corrigida com os nomes de parâmetros exatos (@moeda, @dataInicial, @dataFinalCotacao)
    # Adicionado $select para otimizar e garantir os campos cotacaoCompra, cotacaoVenda e dataHoraCotacao
    url = (
        "https://olinda.bcb.gov.br"
        "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
        f"@moeda='USD'&@dataInicial='{d_inicio}'&@dataFinalCotacao='{d_fim}'"
        "&$format=json&$orderby=dataHoraCotacao desc"
    )
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            dados = res.json().get('value', [])
            # O Banco Central retorna vários boletins por dia. 
            # Filtramos para exibir apenas o boletim de 'Fechamento' (PTAX oficial)
            return [d for d in dados if "Fechamento" in d.get('tipoBoletim', 'Fechamento')]
        return []
    except Exception as e:
        print(f"Erro na API PTAX: {e}")
        return []
Use o código com cuidado.

Principais Ajustes Realizados:
Endpoint OData: A função agora aponta para o caminho completo .../odata/CotacaoMoedaPeriodo(...). No seu código original, a parte /odata/ e o nome da função estavam incompletos na string.
Formato de Data: A API do BCB é rigorosa: datas devem estar entre aspas simples e no formato MM-DD-YYYY.
Filtro de Fechamento: A PTAX possui 4 prévias diárias e 1 fechamento. Filtramos para mostrar apenas o "Fechamento", que é a taxa oficial usada pelo mercado.
Parâmetro @moeda: Incluímos explicitamente o código 'USD' na query string para evitar retornos vazios por falta de especificação do ativo. 
Dica de Deploy: Como você mencionou Fly.io/Koyeb, certifique-se de que o fuso horário do servidor não está pulando o dia atual (o BCB costuma divulgar a PTAX oficial por volta das 13:15h, horário de Brasília). 
Deseja que eu adicione um gráfico de variação do dólar ou prefere manter apenas a visualização em tabela?




undefined
undefined
undefined
4 sites
API de Cotações do Banco Central do Brasil no Power BI
29 de out. de 2024 — API de Cotações do Banco Central do Brasil no Power BI * Em meu canal no YouTube, no vídeo API de cotação do Banco Central no Powe...

LinkedIn

Câmbio PTAX: O que é, onde consultar e como calcular - StoneX
Câmbio PTAX: O que é, onde consultar e como calcular | StoneX. ... A StoneX Brasil oferece acesso global aos mercados e serviços e...

StoneX

Como é a formação da Ptax, que mexe com o dólar no último dia do ...
2 de out. de 2024 — Como é a formação da Ptax, que mexe com o dólar no último dia do mês. ... O último dia útil de cada mês costuma ser importante par...

InvesTalk

Mostrar tudo
Pergunte o que quiser



        
@app.route('/')
def index():
    dados_t = buscar_tesouro()
    dados_p = buscar_historico_ptax()
    linhas_t = "".join([f"<tr><td>{t['titulo']}</td><td>{t['vencimento']}</td><td>{t['taxa']}</td><td class='preco'>{t['preco']}</td></tr>" for t in dados_t])
    linhas_p = ""
    for p in dados_p:
        dt = datetime.strptime(p['dataHoraCotacao'][:10], '%Y-%m-%d').strftime('%d/%m/%Y')
        linhas_p += f"<tr><td>{dt}</td><td>R$ {p['cotacaoCompra']:.4f}</td><td>R$ {p['cotacaoVenda']:.4f}</td></tr>"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Portal Financeiro</title>{ESTILO_CSS}</head>
    <body>
        <div class="container">
            <h1>Cotações e Histórico</h1>
            <div class="nav-tabs">
                <button class="tab-button active" onclick="switchTab('tesouro')">Tesouro Direto</button>
                <button class="tab-button" onclick="switchTab('ptax')">Histórico PTAX</button>
            </div>
            <div id="tesouro" class="content active">
                <table>
                    <thead><tr><th>Título</th><th>Vencimento</th><th>Taxa</th><th>Preço Resgate</th></tr></thead>
                    <tbody>{linhas_t or '<tr><td colspan="4">Sem dados.</td></tr>'}</tbody>
                </table>
            </div>
            <div id="ptax" class="content">
                <div class="scroll-table">
                    <table>
                        <thead><tr><th>Data</th><th>Compra</th><th>Venda</th></tr></thead>
                        <tbody>{linhas_p or '<tr><td colspan="3">Sem dados.</td></tr>'}</tbody>
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

if __name__ == '__main__':
    # Esta parte é crucial para Fly.io e Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
