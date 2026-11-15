# Politique de transformation et valeurs manquantes

Référence CDC F10. Détails : [ADR 002](adr/002-valeurs-manquantes.md).

## Couches

| Couche | Rôle |
|--------|------|
| Bronze | Append NDJSON brut |
| Staging | Nettoyage, validation, `note_transformation` |
| Quarantaine | Lignes rejetées + `motif_rejet` (FR) |
| Gold | Marts en français — voir [dictionnaire-colonnes-fr.md](dictionnaire-colonnes-fr.md) |

## Valeurs manquantes

| Situation | Méthode |
|-----------|---------|
| Champ obligatoire absent | Quarantaine — pas de remplissage |
| `dest_id` pour CASH_IN / CASH_OUT / DEBIT | NULL autorisé |
| `dest_id` pour TRANSFER / PAYMENT | Quarantaine si absent |
| `city` / `operator` vides | Défaut config Togo au producteur ; sinon quarantaine |

## Imputation interdite

Montant, compte, horodatage : jamais remplacés par médiane ou mode global.

## Observations

Textes standard dans `momoshield/transforms/messages_fr.py`.