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
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        titulos = []
        
        # Pega as linhas da tabela
        linhas = soup.find_all('tr')[1:] 

        for linha in linhas:
            cols = linha.find_all('td')
            if len(cols) >= 3:
                titulos.append({
                    "titulo": cols[0].text.strip(),
                    "vencimento": cols[1].text.strip(),
                    "preco": cols[2].text.strip()
                })
        return jsonify(titulos)
    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == '__main__':
    app.run()
