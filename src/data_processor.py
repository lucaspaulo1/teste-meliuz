import pandas as pd

class GrowthDataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        
    def _clean_monetary_column(self, series: pd.Series) -> pd.Series:
        return (series.astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
                .astype(float))

    def load_and_process(self):
        """Carrega e limpa os dados diários, gerando também a versão agrupada."""
        self.df = pd.read_csv(self.file_path)
        
        # Limpeza das colunas financeiras nos dados diários
        for col in ['comissão', 'cashback', 'vendas totais']:
            self.df[col] = self._clean_monetary_column(self.df[col])
            
        # Criação do DataFrame Agrupado (Resumo do Teste)
        grouped = self.df.groupby('Grupos de usuários').agg({
            'Parceiro': 'first',
            'compradores': 'sum',
            'vendas totais': 'sum',
            'comissão': 'sum',
            'cashback': 'sum'
        }).reset_index()
        
        grouped['net_revenue'] = grouped['comissão'] - grouped['cashback']
        grouped['roi_cashback'] = grouped['vendas totais'] / grouped['cashback']
        grouped['ticket_medio'] = grouped['vendas totais'] / grouped['compradores']
        
        # Retorna os dois: o DataFrame diário (limpo) e o agrupado
        return self.df, grouped
