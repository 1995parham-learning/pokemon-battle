"""Battle algorithm for determining Pokemon battle outcomes.

Battle Algorithm Description:
============================

The battle algorithm determines the winner based on a comprehensive scoring system
that considers multiple factors:

1. **Base Stats Power (50% weight)**:
   - Calculates total offensive power: (Attack + Special Attack) / 2
   - Calculates total defensive power: (Defense + Special Defense) / 2
   - Power score = (HP * 0.5 + Offensive + Defensive + Speed) / 4

2. **Type Effectiveness (30% weight)**:
   - Uses Pokemon type matchups to calculate advantage/disadvantage
   - Type effectiveness multiplier ranges from 0.25x to 4x
   - Both Pokemon's types are considered for attack and defense

3. **Speed Advantage (20% weight)**:
   - Faster Pokemon gets a bonus as they would attack first
   - Speed ratio determines the advantage magnitude

Final Calculation:
- Score = (base_power * 0.5) + (type_effectiveness * base_power * 0.3) + (speed_bonus * 0.2)
- The Pokemon with the higher score wins
- In case of a tie (within 1% difference), it's considered a draw

This algorithm balances raw stats with strategic type matchups, similar to
actual Pokemon games but simplified for a single-turn resolution.
"""

from dataclasses import dataclass

from pokemon_battle.models import Pokemon

# Type effectiveness chart (attacking_type -> defending_type -> multiplier)
TYPE_CHART: dict[str, dict[str, float]] = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 2,
        "bug": 2,
        "rock": 0.5,
        "dragon": 0.5,
        "steel": 2,
    },
    "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "electric": {
        "water": 2,
        "electric": 0.5,
        "grass": 0.5,
        "ground": 0,
        "flying": 2,
        "dragon": 0.5,
    },
    "grass": {
        "fire": 0.5,
        "water": 2,
        "grass": 0.5,
        "poison": 0.5,
        "ground": 2,
        "flying": 0.5,
        "bug": 0.5,
        "rock": 2,
        "dragon": 0.5,
        "steel": 0.5,
    },
    "ice": {
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 0.5,
        "ground": 2,
        "flying": 2,
        "dragon": 2,
        "steel": 0.5,
    },
    "fighting": {
        "normal": 2,
        "ice": 2,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 0.5,
        "bug": 0.5,
        "rock": 2,
        "ghost": 0,
        "dark": 2,
        "steel": 2,
        "fairy": 0.5,
    },
    "poison": {
        "grass": 2,
        "poison": 0.5,
        "ground": 0.5,
        "rock": 0.5,
        "ghost": 0.5,
        "steel": 0,
        "fairy": 2,
    },
    "ground": {
        "fire": 2,
        "electric": 2,
        "grass": 0.5,
        "poison": 2,
        "flying": 0,
        "bug": 0.5,
        "rock": 2,
        "steel": 2,
    },
    "flying": {
        "electric": 0.5,
        "grass": 2,
        "fighting": 2,
        "bug": 2,
        "rock": 0.5,
        "steel": 0.5,
    },
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug": {
        "fire": 0.5,
        "grass": 2,
        "fighting": 0.5,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 2,
        "ghost": 0.5,
        "dark": 2,
        "steel": 0.5,
        "fairy": 0.5,
    },
    "rock": {
        "fire": 2,
        "ice": 2,
        "fighting": 0.5,
        "ground": 0.5,
        "flying": 2,
        "bug": 2,
        "steel": 0.5,
    },
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel": {
        "fire": 0.5,
        "water": 0.5,
        "electric": 0.5,
        "ice": 2,
        "rock": 2,
        "steel": 0.5,
        "fairy": 2,
    },
    "fairy": {
        "fire": 0.5,
        "fighting": 2,
        "poison": 0.5,
        "dragon": 2,
        "dark": 2,
        "steel": 0.5,
    },
}


@dataclass
class BattleResult:
    """Result of a Pokemon battle."""

    winner: Pokemon | None
    pokemon1_score: float
    pokemon2_score: float
    battle_log: str
    is_draw: bool


def get_type_effectiveness(attacker_types: list[str], defender_types: list[str]) -> float:
    """
    Calculate type effectiveness multiplier.

    Args:
        attacker_types: List of attacking Pokemon's types.
        defender_types: List of defending Pokemon's types.

    Returns:
        Combined type effectiveness multiplier.
    """
    multiplier = 1.0

    for atk_type in attacker_types:
        atk_chart = TYPE_CHART.get(atk_type, {})
        for def_type in defender_types:
            type_mult = atk_chart.get(def_type, 1.0)
            multiplier *= type_mult

    return multiplier


def calculate_base_power(pokemon: Pokemon) -> float:
    """
    Calculate the base power score for a Pokemon.

    Args:
        pokemon: The Pokemon to calculate power for.

    Returns:
        Base power score.
    """
    offensive = (pokemon.attack + pokemon.special_attack) / 2
    defensive = (pokemon.defense + pokemon.special_defense) / 2

    # Weighted combination of stats
    power = (pokemon.hp * 0.5 + offensive + defensive + pokemon.speed) / 4
    return power


def calculate_battle_score(
    attacker: Pokemon,
    defender: Pokemon,
    attacker_types: list[str],
    defender_types: list[str],
) -> tuple[float, list[str]]:
    """
    Calculate the battle score for an attacking Pokemon.

    Args:
        attacker: The attacking Pokemon.
        defender: The defending Pokemon.
        attacker_types: Attacker's types.
        defender_types: Defender's types.

    Returns:
        Tuple of (score, log_entries).
    """
    log_entries: list[str] = []

    # Base power (50% weight)
    base_power = calculate_base_power(attacker)
    log_entries.append(f"  Base Power: {base_power:.2f}")

    # Type effectiveness (30% weight)
    type_effectiveness = get_type_effectiveness(attacker_types, defender_types)
    type_bonus = type_effectiveness * base_power * 0.3

    if type_effectiveness > 1:
        log_entries.append(f"  Type Advantage: {type_effectiveness:.2f}x (Super Effective!)")
    elif type_effectiveness < 1:
        log_entries.append(f"  Type Disadvantage: {type_effectiveness:.2f}x (Not Very Effective)")
    else:
        log_entries.append("  Type: Neutral")

    # Speed advantage (20% weight)
    speed_ratio = attacker.speed / max(defender.speed, 1)
    speed_bonus = min(speed_ratio, 2.0) * base_power * 0.2

    if attacker.speed > defender.speed:
        log_entries.append(f"  Speed Advantage: {attacker.speed} vs {defender.speed}")
    else:
        log_entries.append(f"  Speed: {attacker.speed} vs {defender.speed}")

    # Final score
    score = (base_power * 0.5) + type_bonus + speed_bonus
    log_entries.append(f"  Final Score: {score:.2f}")

    return score, log_entries


def execute_battle(pokemon1: Pokemon, pokemon2: Pokemon) -> BattleResult:
    """
    Execute a battle between two Pokemon.

    Args:
        pokemon1: The first Pokemon.
        pokemon2: The second Pokemon.

    Returns:
        BattleResult with winner, scores, and battle log.
    """
    log_lines: list[str] = [
        "=" * 50,
        f"BATTLE: {pokemon1.name.upper()} vs {pokemon2.name.upper()}",
        "=" * 50,
        "",
    ]

    # Parse types
    p1_types = [t.strip() for t in pokemon1.types.split(",") if t.strip()]
    p2_types = [t.strip() for t in pokemon2.types.split(",") if t.strip()]

    # Pokemon 1 stats
    p1_sp = f"  SP.ATK: {pokemon1.special_attack} | SP.DEF: {pokemon1.special_defense}"
    log_lines.extend(
        [
            f"{pokemon1.name.upper()} ({', '.join(p1_types)})",
            f"  HP: {pokemon1.hp} | ATK: {pokemon1.attack} | DEF: {pokemon1.defense}",
            f"{p1_sp} | SPD: {pokemon1.speed}",
            "",
        ]
    )

    # Pokemon 2 stats
    p2_sp = f"  SP.ATK: {pokemon2.special_attack} | SP.DEF: {pokemon2.special_defense}"
    log_lines.extend(
        [
            f"{pokemon2.name.upper()} ({', '.join(p2_types)})",
            f"  HP: {pokemon2.hp} | ATK: {pokemon2.attack} | DEF: {pokemon2.defense}",
            f"{p2_sp} | SPD: {pokemon2.speed}",
            "",
        ]
    )

    # Calculate scores
    log_lines.append(f"--- {pokemon1.name.upper()}'s Attack ---")
    score1, log1 = calculate_battle_score(pokemon1, pokemon2, p1_types, p2_types)
    log_lines.extend(log1)
    log_lines.append("")

    log_lines.append(f"--- {pokemon2.name.upper()}'s Attack ---")
    score2, log2 = calculate_battle_score(pokemon2, pokemon1, p2_types, p1_types)
    log_lines.extend(log2)
    log_lines.append("")

    # Determine winner
    log_lines.append("=" * 50)

    # Check for draw (within 1% difference)
    score_diff = abs(score1 - score2)
    avg_score = (score1 + score2) / 2
    is_draw = score_diff < (avg_score * 0.01) if avg_score > 0 else score1 == score2

    if is_draw:
        winner = None
        log_lines.append("RESULT: DRAW!")
        log_lines.append(f"Scores were too close: {score1:.2f} vs {score2:.2f}")
    elif score1 > score2:
        winner = pokemon1
        log_lines.append(f"WINNER: {pokemon1.name.upper()}!")
        log_lines.append(f"Final Scores: {score1:.2f} vs {score2:.2f}")
    else:
        winner = pokemon2
        log_lines.append(f"WINNER: {pokemon2.name.upper()}!")
        log_lines.append(f"Final Scores: {score1:.2f} vs {score2:.2f}")

    log_lines.append("=" * 50)

    return BattleResult(
        winner=winner,
        pokemon1_score=round(score1, 2),
        pokemon2_score=round(score2, 2),
        battle_log="\n".join(log_lines),
        is_draw=is_draw,
    )


class DefaultBattleEngine:
    """Default battle engine using stats-based scoring.

    This engine implements the BattleEngine protocol and uses:
    - Base stats power (50% weight)
    - Type effectiveness (30% weight)
    - Speed advantage (20% weight)
    """

    def execute(self, pokemon1: Pokemon, pokemon2: Pokemon) -> BattleResult:
        """Execute a battle between two Pokemon."""
        return execute_battle(pokemon1, pokemon2)


def get_battle_engine() -> DefaultBattleEngine:
    """Get the default battle engine instance."""
    return DefaultBattleEngine()
