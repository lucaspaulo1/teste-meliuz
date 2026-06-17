import os
import csv
import logging
import pandas as pd

class TrackingService:
    def __init__(self, config: dict):
        self.config = config
        self.csv_file = "consolidado_testes.csv"
        
    def save_result(self, file_name: str, descricao: str, resultado: str, decisao: str):
        """Salva a linha de resultado no Sheets (se configurado) ou faz fallback seguro para CSV."""
        new_row = [file_name, descricao, resultado, decisao]
        headers = ["Nome do Teste", "Descrição", "Resultado", "Decisão Tomada"]
        
        # Lógica de fallback para Google Sheets
        if self.config.get("usar_google_sheets"):
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                
                logging.info("Tentando conectar à API do Google Sheets...")
                scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                # Procura o arquivo JSON de credenciais na raiz
                creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
                client = gspread.authorize(creds)
                
                sheet = client.open(self.config["nome_planilha_google"]).sheet1
                sheet.append_row(new_row)
                logging.info("🚀 Dados registrados com sucesso DIRETAMENTE no Google Sheets público!")
                return
            except Exception as e:
                logging.error(f"Falha ao conectar no Google Sheets ({str(e)}). Executando fallback para CSV local...")

        # Gravação padrão em CSV Local Seguro
        try:
            file_exists = os.path.exists(self.csv_file)
            with open(self.csv_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(headers)
                writer.writerow(new_row)
            logging.info(f"📊 Dados de tracking adicionados ao arquivo local '{self.csv_file}'.")
        except Exception as e:
            logging.error(f"Erro ao salvar tracking local: {str(e)}")
