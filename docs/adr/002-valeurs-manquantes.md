# ADR 002 — Valeurs manquantes (MoMoShield)

## Statut

Accepté — novembre 2026.

## Contexte

PaySim / MoMTSim et le générateur Togo produisent des champs optionnels (`dest_id`) ou enrichissent ville/opérateur. Le CDC interdit l’imputation qui masquerait la fraude.

## Décision

1. **Pas de médiane / moyenne** pour remplir les faits transactionnels silver.
2. **Quarantaine** pour champs obligatoires manquants ou incohérences métier (TRANSFER sans `dest_id`).
3. **NULL métier** conservé (retrait sans destinataire).
4. **Défauts config** (`cities_operators.yaml`) pour enrichissement géographique, pas imputation statistique.
5. **Médiane** uniquement en gold agrégée (`montant_mediane_7j_fcfa` par compte).

## Conséquences

- Module partagé `momoshield.transforms.clean_transaction`.
- Table `quarantine.invalid_transactions`.
- Documentation : `docs/transformation-policy.md`.