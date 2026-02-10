import numpy as np
from scipy.stats import poisson

class StatisticalEngine:
    def __init__(self, df):
        """
        :param df: DataFrame com TODOS os jogos da liga.
        """
        self.df = df
        self.league_avgs = self._calculate_league_averages()

    def _calculate_league_averages(self):
        """Calcula médias globais da liga para Gols, Escanteios e Cartões."""
        return {
            'home_goals': self.df['gols_mandante'].mean(),
            'away_goals': self.df['gols_visitante'].mean(),
            'home_corners': self.df['cantos_mandante'].mean(),
            'away_corners': self.df['cantos_visitante'].mean(),
            'home_cards': self.df['amarelos_mandante'].mean() + self.df['vermelhos_mandante'].mean(),
            'away_cards': self.df['amarelos_visitante'].mean() + self.df['vermelhos_visitante'].mean()
        }

    def calculate_strength(self, team):
        """Calcula Força de Ataque e Defesa (Gols)."""
        # (Código igual ao anterior, mantido para brevidade)
        home_games = self.df[self.df['mandante'] == team]
        if home_games.empty: return None
        
        att_home = home_games['gols_mandante'].mean() / self.league_avgs['home_goals']
        def_home = home_games['gols_visitante'].mean() / self.league_avgs['away_goals']

        away_games = self.df[self.df['visitante'] == team]
        if away_games.empty: return None

        att_away = away_games['gols_visitante'].mean() / self.league_avgs['away_goals']
        def_away = away_games['gols_mandante'].mean() / self.league_avgs['home_goals']

        return {
            'attack_home': att_home, 'defense_home': def_home,
            'attack_away': att_away, 'defense_away': def_away
        }

    def predict_corners_cards(self, home_team, away_team):
        """
        (NOVO - ITEM 3.3) Prevê Escanteios e Cartões usando médias cruzadas.
        Lógica: (Média Favor Mandante + Média Contra Visitante) / 2
        """
        # Filtrar jogos (Home Team em casa e Away Team fora)
        h_games = self.df[self.df['mandante'] == home_team]
        a_games = self.df[self.df['visitante'] == away_team]
        
        if h_games.empty or a_games.empty: return None

        # --- ESCANTEIOS ---
        # Quantos cantos o Mandante costuma ter? vs Quantos o Visitante costuma ceder?
        exp_home_corners = (h_games['cantos_mandante'].mean() + a_games['cantos_visitante'].mean()) / 2
        # Quantos cantos o Visitante costuma ter? vs Quantos o Mandante costuma ceder?
        exp_away_corners = (a_games['cantos_visitante'].mean() + h_games['cantos_mandante'].mean()) / 2
        
        total_corners = exp_home_corners + exp_away_corners

        # --- CARTÕES (Amarelos + Vermelhos) ---
        # Cartões do Mandante + Cartões do Visitante (agressividade dos dois)
        # Aqui somamos as médias de cartões recebidos por ambos
        h_cards = h_games['amarelos_mandante'].mean() + h_games['vermelhos_mandante'].mean()
        a_cards = a_games['amarelos_visitante'].mean() + a_games['vermelhos_visitante'].mean()
        
        total_cards = h_cards + a_cards

        return {
            'exp_corners_home': round(exp_home_corners, 2),
            'exp_corners_away': round(exp_away_corners, 2),
            'exp_corners_total': round(total_corners, 2),
            'exp_cards_total': round(total_cards, 2)
        }

    def predict_match(self, home_team, away_team):
        """Gera todas as previsões (Gols + Secundárias)."""
        # 1. Previsão de Gols (Poisson) - Lógica Anterior
        home_stats = self.calculate_strength(home_team)
        away_stats = self.calculate_strength(away_team)
        
        if not home_stats or not away_stats: return None

        home_xg = home_stats['attack_home'] * away_stats['defense_away'] * self.league_avgs['home_goals']
        away_xg = away_stats['attack_away'] * home_stats['defense_home'] * self.league_avgs['away_goals']

        probs = np.zeros((6, 6))
        for h in range(6):
            for a in range(6):
                probs[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)

        prob_home_win = np.sum(np.tril(probs, -1))
        prob_draw = np.sum(np.diag(probs))
        prob_away_win = np.sum(np.triu(probs, 1))

        # 2. Previsão Secundária (Chamada da nova função)
        secondary = self.predict_corners_cards(home_team, away_team)

        return {
            'home_team': home_team, 'away_team': away_team,
            'lambda_home': round(home_xg, 2),
            'lambda_away': round(away_xg, 2),
            'prob_home': round(prob_home_win * 100, 1),
            'prob_draw': round(prob_draw * 100, 1),
            'prob_away': round(prob_away_win * 100, 1),
            'score_matrix': probs,
            # Adicionamos os dados secundários ao retorno principal
            'secondary_metrics': secondary 
        }

# --- Bloco de Teste ---
if __name__ == "__main__":
    from processor import DataProcessor
    
    # Setup
    proc = DataProcessor()
    df = proc.df
    engine = StatisticalEngine(df)
    
    # Teste Completo
    print("\n🔮 Análise Completa: Liverpool vs Luton")
    prediction = engine.predict_match("Liverpool", "Luton")
    
    # 1. Gols e Probabilidades (O que você sentiu falta)
    print(f"Gols Esperados: {prediction['lambda_home']} x {prediction['lambda_away']}")
    print("-" * 30)
    print(f"Probabilidade Casa:    {prediction['prob_home']}%")
    print(f"Probabilidade Empate:  {prediction['prob_draw']}%")
    print(f"Probabilidade Fora:    {prediction['prob_away']}%")
    print("-" * 30)

    # 2. Métricas Secundárias (Novo)
    sec = prediction['secondary_metrics']
    print(f"Escanteios Esperados:  {sec['exp_corners_total']} (Média Casa: {sec['exp_corners_home']})")
    print(f"Cartões Esperados:     {sec['exp_cards_total']}")