import os
import pandas as pd
from google import genai

class GrowthAIAnalyst:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'

    def generate_report(self, processed_df: pd.DataFrame, validacao: dict) -> str:
        """Gera o relatório de negócios alinhado com o resultado estatístico do sistema."""
        parceiro = processed_df['Parceiro'].iloc[0]
        data_summary = processed_df.to_markdown(index=False)
        
        prompt = f"""
        Você é um Analista de Growth Sênior AI-Native no Méliuz, especialista em testes A/B de cashback.
        Sua tarefa é analisar os resultados consolidados do {parceiro} e gerar um relatório executivo focado em estratégia e dados.
        
        Dados Consolidados do Teste:
        {data_summary}
        
        Veredito do Mecanismo Estatístico (Teste T de Student sobre dados diários):
        - Variante com maior Lucro Acumulado: {validacao['vencedor_preliminar']}
        - A diferença é estatisticamente significante? {"Sim" if validacao['significativo'] else "Não"}
        - p-valor calculado: {validacao['p_value']:.4f}
        - Decisão Recomendada pelo Sistema: {validacao['decisao_tomada']}
        
        Instruções para o Relatório (Gere em formato Markdown):
        1. Resumo Executivo: Visão geral da performance do parceiro.
        2. Análise Crítica das Variantes: Discuta os grupos. Explique o conceito de "falso vencedor" baseado no custo do cashback vs lucro líquido.
        3. Validação Estatística: Explique ao gestor o significado técnico do p-valor encontrado ({validacao['p_value']:.4f}) e por que analisar apenas a soma acumulada pode ser perigoso para a operação do Méliuz.
        4. Decisão Acionável Conclusiva: Siga rigorosamente a recomendação do sistema: "{validacao['decisao_tomada']}".
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text
