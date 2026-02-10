import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Gerencia a coleta de dados de múltiplas ligas via Football-Data.co.uk.
    """
    
    BASE_URL = "https://www.football-data.co.uk/mmz4281/2526/{}.csv"
    
    # Dicionário de Ligas Disponíveis (Nome: Código)
    LEAGUES = {
        "Premier League (Inglaterra)": "E0",
        "Championship (Inglaterra 2ª)": "E1",
        "La Liga (Espanha)": "SP1",
        "Serie A (Itália)": "I1",
        "Bundesliga (Alemanha)": "D1",
        "Ligue 1 (França)": "F1",
        "Liga Portugal (Portugal)": "P1",
        "Eredivisie (Holanda)": "N1"
    }
    
    def __init__(self):
        self.raw_data = None
        
    def load_data(self, league_name):
        """
        Baixa os dados da liga selecionada.
        :param league_name: Chave do dicionário LEAGUES (ex: 'La Liga (Espanha)')
        """
        code = self.LEAGUES.get(league_name)
        if not code:
            print(f"❌ Liga '{league_name}' não encontrada.")
            return None

        url = self.BASE_URL.format(code)
        print(f"🔄 Baixando dados da {league_name}: {url} ...")
        
        try:
            self.raw_data = pd.read_csv(url)
            print(f"✅ Download concluído! {len(self.raw_data)} jogos carregados.")
            return self.raw_data
        except Exception as e:
            print(f"❌ Erro ao baixar dados: {e}")
            return None

    def save_local(self, league_name):
        """Salva o arquivo com um nome específico para cada liga."""
        if self.raw_data is not None:
            Path("data").mkdir(exist_ok=True)
            
            # Cria um nome de arquivo seguro (ex: la_liga_espanha_2526.csv)
            safe_name = league_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            filename = f"data/{safe_name}_2526.csv"
            
            self.raw_data.to_csv(filename, index=False)
            print(f"💾 Arquivo salvo em: {filename}")
            return filename
        return None