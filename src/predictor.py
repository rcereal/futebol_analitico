import numpy as np

class BetAdvisor:
    def __init__(self, statistical_engine):
        self.engine = statistical_engine

    def get_match_suggestion(self, home_team, away_team):
        """
        Analisa probabilidades e gera dicas com ODD JUSTA.
        """
        # 1. Obter previsões matemáticas
        prediction = self.engine.predict_match(home_team, away_team)
        
        if not prediction:
            return {"erro": "Dados insuficientes para análise."}

        tips = []
        
        # --- Lógica 1: Vencedor (Match Odds) ---
        prob_home = prediction['prob_home']
        prob_away = prediction['prob_away']
        
        if prob_home >= 55:
            tips.append({
                "mercado": "Vencedor",
                "selecao": f"Vitória {home_team}",
                "probabilidade": f"{prob_home}%",
                "odd_justa": round(100 / prob_home, 2), # CÁLCULO DA ODD
                "confianca": "Alta" if prob_home > 65 else "Média"
            })
        elif prob_away >= 55:
            tips.append({
                "mercado": "Vencedor",
                "selecao": f"Vitória {away_team}",
                "probabilidade": f"{prob_away}%",
                "odd_justa": round(100 / prob_away, 2), # CÁLCULO DA ODD
                "confianca": "Alta" if prob_away > 65 else "Média"
            })

        # --- Lógica 2: Gols (Over 2.5) ---
        matrix = prediction['score_matrix']
        prob_over_25 = 0
        for h in range(6):
            for a in range(6):
                if (h + a) > 2.5: prob_over_25 += matrix[h, a]
        
        prob_over_25 = round(prob_over_25 * 100, 1)
        
        if prob_over_25 >= 60:
            tips.append({
                "mercado": "Gols",
                "selecao": "Over 2.5 Gols",
                "probabilidade": f"{prob_over_25}%",
                "odd_justa": round(100 / prob_over_25, 2), # CÁLCULO DA ODD
                "confianca": "Alta" if prob_over_25 > 70 else "Média"
            })

        # --- Lógica 3: Ambas Marcam (BTTS) ---
        prob_btts = 0
        for h in range(1, 6):
            for a in range(1, 6):
                prob_btts += matrix[h, a]
        prob_btts = round(prob_btts * 100, 1)

        if prob_btts >= 60:
            tips.append({
                "mercado": "Gols",
                "selecao": "Ambas Marcam: Sim",
                "probabilidade": f"{prob_btts}%",
                "odd_justa": round(100 / prob_btts, 2), # CÁLCULO DA ODD
                "confianca": "Média"
            })

        # --- Lógica 4: Escanteios ---
        sec = prediction['secondary_metrics']
        exp_corners = sec['exp_corners_total']
        
        if exp_corners >= 10.5:
             tips.append({
                "mercado": "Escanteios",
                "selecao": "Over 9.5 Cantos",
                "probabilidade": f"Média esperada: {exp_corners}",
                "odd_justa": "-", # Não aplicável
                "confianca": "Média"
            })

        # --- Lógica 5: Cartões ---
        exp_cards = sec['exp_cards_total']
        
        if exp_cards >= 4.5:
             tips.append({
                "mercado": "Cartões",
                "selecao": "Over 3.5 Cartões",
                "probabilidade": f"Média esperada: {exp_cards}",
                "odd_justa": "-", # Não aplicável
                "confianca": "Baixa"
            })

        return {
            "match": f"{home_team} vs {away_team}",
            "stats": prediction,
            "sugestoes": tips
        }

# --- Bloco de Teste ---
if __name__ == "__main__":
    from processor import DataProcessor
    from analyzer import StatisticalEngine
    
    proc = DataProcessor()
    df = proc.df
    engine = StatisticalEngine(df)
    advisor = BetAdvisor(engine)
    
    # Teste
    print("\n🎲 Analisando: Chelsea vs Tottenham")
    analise = advisor.get_match_suggestion("Chelsea", "Tottenham")
    
    for tip in analise['sugestoes']:
        print(f"💰 {tip['mercado']}: {tip['selecao']} (Odd Justa: {tip['odd_justa']})")