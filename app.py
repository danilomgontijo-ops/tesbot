import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permite que sites externos (seu app web) acessem esta API
CORS(app)

@app.route('/')
def home():
    return "API Tesouro Online! Vá para /precos para ver as cotações."

@app.route('/precos')
def extrair_precos():
    # URL específica que você forneceu
    url = "https://ghostnetrn.github.io/bot-tesouro-direto/"
    
    # Simula um navegador real para o site não bloquear o Render
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # Garante que acentos não fiquem estranhos
        
        soup = BeautifulSoup(response.text, 'html.parser')
        lista_titulos = []
        
        # O site usa uma tabela. Vamos buscar todas as linhas (tr)
        tabela = soup.find('table')
        if not tabela:
            return jsonify({"erro": "Tabela de preços não encontrada no site"})

        linhas = tabela.find_all('tr')

        for linha in linhas:
            colunas = linha.find_all('td')
            
            # Verificamos se a linha tem as colunas necessárias (Título, Vencimento, Taxa, Preço)
            if len(colunas) >= 4:
                dados = {
                    "titulo": colunas[0].get_text(strip=True),
                    "vencimento": colunas[1].get_text(strip=True),
                    "taxa_rendimento": colunas[2].get_text(strip=True),
                    "preco_resgate": colunas[3].get_text(strip=True) # Este é o valor de venda
                }
                lista_titulos.append(dados)

        return jsonify(lista_titulos)

    except Exception as e:
        return jsonify({"erro": f"Falha na extração: {str(e)}"})

if __name__ == '__main__':
    # O Render define a porta automaticamente, por isso não fixamos 5000
    app.run()
