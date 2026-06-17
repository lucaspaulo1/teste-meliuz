import sys
import os
import json
import logging
from dotenv import load_dotenv
from src.data_processor import GrowthDataProcessor
from src.ai_analyst import GrowthAIAnalyst
from src.statistical_validator import GrowthStatisticalValidator
from src.sheets_service import TrackingService

# Configuração profissional do Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

load_dotenv()

def carregar_configuracao():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Arquivo 'config.json' não encontrado. Usando parâmetros default.")
        return {"alpha_significancia": 0.05, "salvar_graficos": True, "usar_google_sheets": False}

def main():
    if len(sys.argv) < 2:
        logging.error("Uso incorreto do CLI. Formato correto: python main.py <caminho_do_dataset.csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        logging.error(f"Arquivo de input não encontrado: {file_path}")
        sys.exit(1)
        
    file_name = os.path.basename(file_path)
    config = carregar_configuracao()
    output_dir = config.get("diretorio_outputs", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    logging.info(f"Iniciando pipeline de processamento para: {file_name}")
    
    try:
        # 1. ETL e Processamento de Dados
        processor = GrowthDataProcessor(file_path)
        df_diario, metrics_df = processor.load_and_process()
        
        # 2. Validação Estatística Conforme Configuração
        validator = GrowthStatisticalValidator(
            alpha=config.get("alpha_significancia", 0.05),
            salvar_grafico=config.get("salvar_graficos", True)
        )
        validacao = validator.validate_test(df_diario, output_dir=output_dir)
        
        # 3. Análise Cognitiva via LLM (Com Tratamento de Erros Isolado)
        report = ""
        try:
            logging.info("Chamando API da LLM para geração do relatório...")
            analyst = GrowthAIAnalyst()
            report = analyst.generate_report(metrics_df, validacao)
            
            # Incorpora o caminho do gráfico gerado dentro do relatório final Markdown
            if validacao["chart_path"]:
                report += f"\n\n### Evidência Visual da Distribuição\n![Distribuição de Margem]({os.path.basename(validacao['chart_path'])})\n"
                
            print("\n" + "="*50 + "\n📜 OUTPUT DO RELATÓRIO DA IA\n" + "="*50)
            print(report)
            print("="*50 + "\n")
            
            report_path = os.path.join(output_dir, f"relatorio_{file_name.replace('.csv', '.md')}")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            logging.info(f"Relatório executivo exportado com sucesso em: {report_path}")
            
        except Exception as ai_error:
            # Captura a instabilidade da API (ex: erro 503) sem derrubar o programa inteiro
            logging.error(f"⚠️ Falha temporária na API do Gemini: {str(ai_error)}. O pipeline avançará usando as métricas determinísticas.")
            logging.info("A gravação dos dados de tracking não será afetada.")
        
        # 4. Gravação de Tracking de Resultados (Sempre executa, independente da IA)
        parceiro = metrics_df['Parceiro'].iloc[0]
        tracker = TrackingService(config)
        tracker.save_result(
            file_name=file_name,
            descricao=f"Teste A/B de variação de cashback para o {parceiro}.",
            resultado=validacao['resultado_resumido'],
            decisao=validacao['decisao_tomada']
        )
        logging.info("Pipeline executado com sucesso de ponta a ponta.")
        
    except Exception as e:
        logging.critical(f"Falha catastrófica irreversível na execução do pipeline: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
