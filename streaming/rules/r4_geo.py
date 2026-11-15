from __future__ import annotations

from streaming.rules.types import AccountState, RuleConfig, RuleHit, TransactionView

# Distances approximatives (minutes de trajet min) entre villes du Togo (simplifié)
CITY_DISTANCE_MINUTES: dict[tuple[str, str], float] = {
    ("Lomé", "Kara"): 420,
    ("Lomé", "Sokodé"): 300,
    ("Kara", "Dapaong"): 180,
}


def travel_minutes(city_a: str, city_b: str) -> float:
    if city_a == city_b:
        return 0.0
    key = (city_a, city_b)
    rev = (city_b, city_a)
    if key in CITY_DISTANCE_MINUTES:
        return CITY_DISTANCE_MINUTES[key]
    if rev in CITY_DISTANCE_MINUTES:
        return CITY_DISTANCE_MINUTES[rev]
    return 120.0


def check_r4_geo(tx: TransactionView, state: AccountState, cfg: RuleConfig) -> RuleHit | None:
    if not state.last_city or not state.last_city_time:
        return None
    if state.last_city == tx.city:
        return None
    elapsed = (tx.event_time - state.last_city_time).total_seconds() / 60.0
    needed = travel_minutes(state.last_city, tx.city)
    if elapsed < needed and elapsed < cfg.geo_min_minutes:
        score = min(1.0, (needed - elapsed) / needed)
        return RuleHit(
            rule_id="R4",
            score=score,
            context={
                "from_city": state.last_city,
                "to_city": tx.city,
                "elapsed_min": elapsed,
                "min_travel_min": needed,
            },
        )
    return None