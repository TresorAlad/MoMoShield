# Limites du jeu PaySim

- Dataset : [PaySim sur Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1) — `make download-paysim`.
- Version Kaggle ≈ 25 % du simulateur d'origine.
- Fraude native ~0,1 % → **injection F3** requise pour l'évaluation.
- Colonnes soldes (`oldbalanceOrg`, etc.) : **ne pas utiliser** pour la détection (fuite).
- Conversion montant → FCFA : **fictive** (×600 documenté).
- Référence : Lopez-Rojas, Elmir & Axelsson, *PaySim*, EMSS 2016.