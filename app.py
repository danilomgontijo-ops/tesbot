from fastapi import FastAPI
import pandas as pd
import requests
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

app = FastAPI()

# Endpoint para taxas de resgate do Tesouro Direto
@app.get("/tesouro-resgate")
def get_tesouro_resgate():
    url = "https://raw.githubusercontent.com/ghostnetrn/bot-tesouro-direto/refs/heads/main/rendimento_resgatar.csv"
    try:
        df = pd.read_csv(url, sep=';', decimal=',')  # Ajuste separador e decimal se necessário (comum em CSVs brasileiros)
        # Converter DataFrame para lista de dicionários para JSON
        data = df.to_dict(orient='records')
        return {"status": "success", "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Endpoint para cotação do dólar PTAX dos últimos 12 meses
@app.get("/dolar-ptax")
def get_dolar_ptax():
    # Calcular datas: últimos 12 meses
    end_date = datetime.now().strftime("%m-%d-%Y")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%m-%d-%Y")  # Aproximadamente 12 meses
    
    # API do Banco Central do Brasil (BCB) para PTAX (cotação de fechamento)
    bcb_url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{start_date}'&@dataFinalCotacao='{end_date}'&$top=10000&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
    
    try:
        response = requests.get(bcb_url)
        response.raise_for_status()
        data = response.json()['value']
        # Ordenar por data descending (mais recente primeiro)
        data_sorted = sorted(data, key=lambda x: x['dataHoraCotacao'], reverse=True)
        return {"status": "success", "data": data_sorted}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Rodar localmente com: uvicorn main:app --reload
