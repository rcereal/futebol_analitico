import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Gerencia a coleta de dados via Football-Data.co.uk.
    Fonte robusta que fornece CSVs com estatísticas detalhadas e odds.
    """
    
    # ATUALIZADO: Temporada 25/26 (2025/2026)
    # Padrão do site: mmz4281/{temporada}/E0.csv
    DATA_URL = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
    
    def __init__(self):
        self.raw_data = None
        
    def load_data(self):
        """Baixa e carrega os dados da Premier League Atual."""
        print(f"🔄 Baixando dados da Temporada 25/26: {self.DATA_URL} ...")
        
        try:
            self.raw_data = pd.read_csv(self.DATA_URL)
            print(f"✅ Download concluído! {len(self.raw_data)} jogos carregados.")
            return self.raw_data
            
        except Exception as e:
            print(f"❌ Erro ao baixar dados: {e}")
            return None

    def save_local(self, filename="premier_league_2526.csv"):
        """Salva com o nome da nova temporada."""
        if self.raw_data is not None:
            # Garante que a pasta data existe
            Path("data").mkdir(exist_ok=True)
            
            filepath = Path(f"data/{filename}")
            self.raw_data.to_csv(filepath, index=False)
            print(f"💾 Arquivo salvo em: {filepath}")

if __name__ == "__main__":
    loader = DataLoader()
    df = loader.load_data()
    if df is not None:
        loader.save_local()