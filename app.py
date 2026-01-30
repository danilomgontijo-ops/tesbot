import requests
import csv
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API Tesouro CSV Online! Vá para /precos"

@app.route('/precos')
def extrair_precos():
    # URL do arquivo RAW (importante ser a versão raw.githubusercontent)
    url_csv = "https://raw.githubusercontent.com"
    
    try:
        response = requests.get(url_csv)
        response.encoding = 'utf-8' # Para não bugar os acentos
        
        if response.status_code != 200:
            return jsonify({"erro": "Não foi possível carregar o CSV"}), 500
        
        # O CSV usa ";" como separador conforme você indicou
        conteudo = response.text.strip().split('\n')
        leitor = csv.reader(conteudo, delimiter=';')
        
        titulos = []
        for linha in leitor:
            if len(linha) >= 4:
                titulos.append({
                    "titulo": linha[0],        # Tesouro Prefixado 2027Juros Semestrais
                    "taxa": linha[1],          # 13,66%
                    "preco_resgate": linha[2], # R$ 978,45
                    "vencimento": linha[3]     # 01/01/2027
                })
        
        return jsonify(titulos)

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar CSV: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()
