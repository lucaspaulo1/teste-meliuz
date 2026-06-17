import sys
import os
import pandas as pd
from dotenv import load_dotenv
from src.data_processor import GrowthDataProcessor
from src.ai_analyst import GrowthAIAnalyst
from src.statistical_validator import GrowthStatisticalValidator

load_dotenv()

def update_tracking_sheet(file_name, descricao, resultado, decisao):
    """Atualiza a planilha de tracking local atendendo todos os requisitos do edital."""
    tracking_file = "consolidado_testes.csv"
    new_row = {
        "Nome do Teste": file_name,
        "Descrição": descricao,
        "Resultado": resultado,
        "Decisão Tomada": decisao
    }
    
    if os.path.exists(tracking_file):
        df_track = pd.read_csv(tracking_file)
        df_track = pd.concat([df_track, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df_track = pd.DataFrame([new_row])
        
    df_track.to_csv(tracking_file, index=False)
    print(f"📊 Tracking atualizado com sucesso em '{tracking_file}'!")

def main():
    if len(sys.argv) < 2:
        print("Uso correto: python main.py <caminho_do_dataset.csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    file_name = os.path.basename(file_path)
    
    print(f"🚀 Iniciando análise avançada do arquivo: {file_name}...\n")
    
    # 1. Pipeline de Dados
    processor = GrowthDataProcessor(file_path)
    df_diario, metrics_df = processor.load_and_process()
    
    # 2. Validação Estatística (Rigor Científico)
    validator = GrowthStatisticalValidator()
    validacao = validator.validate_test(df_diario)
    
    # 3. Geração de Relatório Cognitivo via LLM
    analyst = GrowthAIAnalyst()
    report = analyst.generate_report(metrics_df, validacao)
    
    # Exibe o relatório gerado
    print("="*40 + "\n📜 RELATÓRIO DA IA GENERATIVA\n" + "="*40)
    print(report)
    print("="*40 + "\n")
    
    # Salva o arquivo Markdown local
    report_output_path = f"relatorio_{file_name.replace('.csv', '.md')}"
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📁 Relatório executivo salvo em: {report_output_path}")
    
    # 4. Gravação de Metadados Completos na Planilha
    parceiro = metrics_df['Parceiro'].iloc[0]
    descricao_teste = f"Teste A/B de incentivo de cashback para o {parceiro}."
    
    update_tracking_sheet(
        file_name=file_name,
        descricao=descricao_teste,
        resultado=validacao['resultado_resumido'],
        decisao=validacao['decisao_tomada']
    )

if __name__ == "__main__":
    main()
