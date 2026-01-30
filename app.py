import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API Online! Acesse /precos para ver os dados."

@app.route('/precos')
def extrair_precos():
    url = "https://ghostnetrn.github.io"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        titulos = []
        
        # Pega as linhas da tabela (ajuste o seletor da tabela se necessário)
        linhas = soup.find_all('tr')[1:] 

        for linha in linhas:
            cols = linha.find_all('td')
            if len(cols) >= 4: # Verifica se tem pelo menos 4 colunas (Título, Vencimento, Preço Compra, Preço Venda)
                titulos.append({
                    "titulo": cols[0].text.strip(),
                    "vencimento": cols[1].text.strip(),
                    # Vamos tentar pegar a terceira ou quarta coluna para o preço
                    "preco_compra": cols[2].text.strip(),
                    "preco_venda": cols[3].text.strip()
                })
        return jsonify(titulos)
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == '__main__':
    app.run()
