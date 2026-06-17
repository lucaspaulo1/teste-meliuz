import os
import logging
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

class GrowthStatisticalValidator:
    def __init__(self, alpha: float = 0.05, salvar_grafico: bool = True):
        self.alpha = alpha
        self.salvar_grafico = salvar_grafico

    def validate_test(self, df_diario: pd.DataFrame, output_dir: str = "outputs") -> dict:
        """Executa teste de hipótese sobre o Net Revenue diário e gera evidências visuais."""
        try:
            logging.info("Iniciando validação estatística dos dados diários...")
            df_diario['net_revenue_diario'] = df_diario['comissão'] - df_diario['cashback']
            
            totais = df_diario.groupby('Grupos de usuários')['net_revenue_diario'].sum().sort_values(ascending=False)
            
            if len(totais) < 2:
                raise ValueError("O dataset não possui variantes suficientes para comparação estatística.")
                
            grupo_1st = totais.index[0]
            grupo_2nd = totais.index[1]
            
            # Coleta as séries diárias corrigindo o NameError anterior
            dados_1st = df_diario[df_diario['Grupos de usuários'] == grupo_1st]['net_revenue_diario']
            dados_2nd = df_diario[df_diario['Grupos de usuários'] == grupo_2nd]['net_revenue_diario']
            
            # Teste T de Welch (amostras independentes com variâncias possivelmente desiguais)
            t_stat, p_val = stats.ttest_ind(dados_1st, dados_2nd, equal_var=False)
            significativo = p_val < self.alpha
            
            decisao = f"Escalar {grupo_1st}" if significativo else f"Empate Técnico - Manter {grupo_1st} por menor risco"
            resultado_resumido = f"{grupo_1st} (R$ {totais.iloc[0]:,.2f}) vs {grupo_2nd} (R$ {totais.iloc[1]:,.2f}) | p-valor: {p_val:.4f}"
            
            # Geração de Gráfico (Diferencial)
            chart_path = ""
            if self.salvar_grafico:
                os.makedirs(output_dir, exist_ok=True)
                plt.figure(figsize=(8, 5))
                df_diario.boxplot(column='net_revenue_diario', by='Grupos de usuários', grid=False)
                plt.title('Distribuição Diária de Net Revenue por Variante')
                plt.suptitle('')
                plt.ylabel('Net Revenue (R$)')
                chart_path = os.path.join(output_dir, 'distribuicao_net_revenue.png')
                plt.savefig(chart_path)
                plt.close()
                logging.info(f"Gráfico de diagnóstico salvo com sucesso em: {chart_path}")
            
            return {
                "vencedor_preliminar": grupo_1st,
                "significativo": significativo,
                "p_value": p_val,
                "decisao_tomada": decisao,
                "resultado_resumido": resultado_resumido,
                "chart_path": chart_path
            }
            
        except Exception as e:
            logging.error(f"Erro crítico durante a validação estatística: {str(e)}")
            raise e
