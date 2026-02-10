import numpy as np
from scipy.stats import poisson

class StatisticalEngine:
    def __init__(self, df):
        """
        :param df: DataFrame com TODOS os jogos da liga (para calcular médias globais).
        """
        self.df = df
        self.league_avgs = self._calculate_league_averages()

    def _calculate_league_averages(self):
        """Calcula a média de gols Mandante e Visitante de TODA a liga."""
        # Média de gols feitos pelos mandantes
        avg_home = self.df['gols_mandante'].mean()
        # Média de gols feitos pelos visitantes
        avg_away = self.df['gols_visitante'].mean()
        
        return {'home_goals': avg_home, 'away_goals': avg_away}

    def calculate_strength(self, team):
        """
        Calcula a Força de Ataque e Defesa de um time baseado na temporada toda.
        Retorna: {attack_home, defense_home, attack_away, defense_away}
        """
        # Jogos em Casa
        home_games = self.df[self.df['mandante'] == team]
        if home_games.empty: return None # Evita divisão por zero
        
        att_home = home_games['gols_mandante'].mean() / self.league_avgs['home_goals']
        def_home = home_games['gols_visitante'].mean() / self.league_avgs['away_goals']

        # Jogos Fora
        away_games = self.df[self.df['visitante'] == team]
        if away_games.empty: return None

        att_away = away_games['gols_visitante'].mean() / self.league_avgs['away_goals']
        def_away = away_games['gols_mandante'].mean() / self.league_avgs['home_goals']

        return {
            'attack_home': att_home, 'defense_home': def_home,
            'attack_away': att_away, 'defense_away': def_away
        }

    def predict_match(self, home_team, away_team):
        """
        Usa Distribuição de Poisson para prever as probabilidades do jogo.
        """
        # 1. Pegar forças
        home_stats = self.calculate_strength(home_team)
        away_stats = self.calculate_strength(away_team)
        
        if not home_stats or not away_stats:
            return None

        # 2. Calcular Expectativa de Gols (Lambda)
        # Exp. Mandante = Ataque Mandante x Defesa Visitante x Média Liga
        home_xg = home_stats['attack_home'] * away_stats['defense_away'] * self.league_avgs['home_goals']
        
        # Exp. Visitante = Ataque Visitante x Defesa Mandante x Média Liga
        away_xg = away_stats['attack_away'] * home_stats['defense_home'] * self.league_avgs['away_goals']

        # 3. Simular Placar (Matriz de Probabilidades 0x0 até 5x5)
        probs = np.zeros((6, 6)) # Matriz 6x6
        for h in range(6): # 0 a 5 gols
            for a in range(6):
                # Probabilidade de H gols * Probabilidade de A gols
                p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                probs[h, a] = p

        # 4. Somar probabilidades para 1x2 (Home, Draw, Away)
        prob_home_win = np.sum(np.tril(probs, -1)) # Soma triângulo inferior
        prob_draw = np.sum(np.diag(probs))         # Soma diagonal
        prob_away_win = np.sum(np.triu(probs, 1))  # Soma triângulo superior

        return {
            'home_team': home_team,
            'away_team': away_team,
            'lambda_home': round(home_xg, 2), # Gols esperados Mandante
            'lambda_away': round(away_xg, 2), # Gols esperados Visitante
            'prob_home': round(prob_home_win * 100, 1),
            'prob_draw': round(prob_draw * 100, 1),
            'prob_away': round(prob_away_win * 100, 1),
            'score_matrix': probs # Matriz bruta para uso futuro (Over/Under)
        }

# --- Bloco de Teste ---
if __name__ == "__main__":
    from processor import DataProcessor
    
    # Carrega dados
    proc = DataProcessor()
    df = proc.df
    
    # Inicializa Motor Estatístico
    engine = StatisticalEngine(df)
    
    # Simula um clássico
    print("\n🔮 Previsão Estatística: Man City (Casa) vs Arsenal (Fora)")
    prediction = engine.predict_match("Man City", "Arsenal")
    
    print(f"Gols Esperados City: {prediction['lambda_home']}")
    print(f"Gols Esperados Arsenal: {prediction['lambda_away']}")
    print("-" * 30)
    print(f"Probabilidade City Vencer: {prediction['prob_home']}%")
    print(f"Probabilidade Empate:      {prediction['prob_draw']}%")
    print(f"Probabilidade Arsenal Vencer: {prediction['prob_away']}%")