import requests
import csv
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Aumenta o limite de tamanho de campo do CSV para evitar o erro de "field larger than field limit"
csv.field_size_limit(sys.maxsize)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API Tesouro CSV Online! Vá para /precos"

@app.route('/precos')
def extrair_precos():
    # URL do arquivo RAW correta
    url_csv = "https://raw.githubusercontent.com"
    
    try:
        response = requests.get(url_csv)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return jsonify({"erro": "Não foi possível carregar o arquivo no GitHub"}), 500
        
        # Limpa espaços em branco extras e divide por linhas
        linhas_sujas = response.text.strip().splitlines()
        
        titulos = []
        # Processa cada linha individualmente para evitar que o CSV engasgue
        for linha_texto in linhas_sujas:
            # Divide manualmente pelo ponto e vírgula
            partes = linha_texto.split(';')
            
            if len(partes) >= 4:
                titulos.append({
                    "titulo": partes[0].strip(),
                    "taxa": partes[1].strip(),
                    "preco_resgate": partes[2].strip(),
                    "vencimento": partes[3].strip()
                })
        
        return jsonify(titulos)

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar dados: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()
