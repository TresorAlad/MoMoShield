"""Messages d'observation et quarantaine (français)."""

from __future__ import annotations

MOTIF_CHAMP_OBLIGATOIRE = "Champ obligatoire manquant"
MOTIF_TYPE_INVALIDE = "Type d'opération invalide"
MOTIF_OPERATEUR_INVALIDE = "Opérateur invalide"
MOTIF_MONTANT_INVALIDE = "Montant manquant ou non positif"
MOTIF_DEST_MANQUANT = "Destinataire manquant pour transfert ou paiement"
MOTIF_VALIDATION_CONTRAT = "Échec validation contrat transaction_v1"

OBS_DEST_AUTORISE_NULL = "Pas de destinataire — normal pour cette opération"
OBS_VILLE_DEFAUT = "Ville complétée depuis configuration Togo"
OBS_MEDIANE_AGREGAT = (
    "Médiane sur historique — non utilisée pour imputer les transactions"
)


def observation_technique(champ: str, valeur: str | None) -> str:
    val = (valeur or "")[:80]
    return f"Champ {champ}, valeur reçue : {val!r}"