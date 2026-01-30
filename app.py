import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API Tesouro Rodando! Acesse /precos"

@app.route('/precos')
def extrair_precos():
    # URL alvo
    url = "https://github.com/ghostnetrn/bot-tesouro-direto/blob/main/rendimento_resgatar.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        # Se o site falhar, tentamos forçar a leitura
        soup = BeautifulSoup(response.content, 'html.parser')
        
        titulos = []
        
        # O site alvo usa tabelas padrão HTML. Vamos buscar todas.
        tabelas = soup.find_all('table')
        
        for tabela in tabelas:
            linhas = tabela.find_all('tr')
            for linha in linhas:
                cols = linha.find_all('td')
                if len(cols) >= 3:
                    # Limpando os textos de espaços e caracteres vazios
                    nome = cols[0].get_text(strip=True)
                    vencimento = cols[1].get_text(strip=True)
                    # No Tesouro, geralmente a última ou penúltima coluna é o preço
                    preco = cols[-1].get_text(strip=True) 
                    
                    # Filtro para ignorar cabeçalhos ou linhas vazias
                    if "Título" not in nome and "Preço" not in nome:
                        titulos.append({
                            "titulo": nome,
                            "vencimento": vencimento,
                            "preco_resgate": preco
                        })

        if not titulos:
            return jsonify({"mensagem": "Site acessado, mas nenhuma tabela foi encontrada. Verifique se o site mudou o layout."}), 404

        return jsonify(titulos)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run()
