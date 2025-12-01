"""Tests for the battle algorithm."""


from pokemon_battle.battle import (
    calculate_base_power,
    execute_battle,
    get_type_effectiveness,
)
from pokemon_battle.models import Pokemon


class TestTypeEffectiveness:
    """Tests for type effectiveness calculations."""

    def test_super_effective(self) -> None:
        """Test super effective type matchup."""
        # Fire is super effective against Grass
        effectiveness = get_type_effectiveness(["fire"], ["grass"])
        assert effectiveness == 2.0

    def test_not_very_effective(self) -> None:
        """Test not very effective type matchup."""
        # Fire is not very effective against Water
        effectiveness = get_type_effectiveness(["fire"], ["water"])
        assert effectiveness == 0.5

    def test_neutral(self) -> None:
        """Test neutral type matchup."""
        # Normal vs Fighting (no special interaction)
        effectiveness = get_type_effectiveness(["normal"], ["fighting"])
        assert effectiveness == 1.0

    def test_immune(self) -> None:
        """Test immunity type matchup."""
        # Normal cannot hit Ghost
        effectiveness = get_type_effectiveness(["normal"], ["ghost"])
        assert effectiveness == 0.0

    def test_dual_type_defender(self) -> None:
        """Test effectiveness against dual type defender."""
        # Electric vs Water/Flying (both super effective)
        effectiveness = get_type_effectiveness(["electric"], ["water", "flying"])
        assert effectiveness == 4.0

    def test_dual_type_attacker(self) -> None:
        """Test effectiveness with dual type attacker."""
        # Fire/Flying vs Grass
        effectiveness = get_type_effectiveness(["fire", "flying"], ["grass"])
        assert effectiveness == 4.0  # Both are super effective


class TestBasePower:
    """Tests for base power calculations."""

    def test_base_power_calculation(self, pikachu: Pokemon) -> None:
        """Test base power calculation for Pikachu."""
        power = calculate_base_power(pikachu)
        # Offensive: (55 + 50) / 2 = 52.5
        # Defensive: (40 + 50) / 2 = 45
        # Power: (35 * 0.5 + 52.5 + 45 + 90) / 4 = 51.25
        assert abs(power - 51.25) < 0.01

    def test_base_power_higher_stats(self, charizard: Pokemon) -> None:
        """Test that higher stats result in higher power."""
        pikachu = Pokemon(
            id=1,
            pokeapi_id=25,
            name="pikachu",
            hp=35,
            attack=55,
            defense=40,
            special_attack=50,
            special_defense=50,
            speed=90,
            types="electric",
        )
        pikachu_power = calculate_base_power(pikachu)
        charizard_power = calculate_base_power(charizard)
        assert charizard_power > pikachu_power


class TestExecuteBattle:
    """Tests for battle execution."""

    def test_battle_has_winner(self, pikachu: Pokemon, charizard: Pokemon) -> None:
        """Test that a battle produces a winner."""
        result = execute_battle(pikachu, charizard)
        # Charizard should generally win due to higher stats
        assert result.winner is not None or result.is_draw

    def test_battle_scores_calculated(self, pikachu: Pokemon, charizard: Pokemon) -> None:
        """Test that battle scores are calculated."""
        result = execute_battle(pikachu, charizard)
        assert result.pokemon1_score > 0
        assert result.pokemon2_score > 0

    def test_battle_log_generated(self, pikachu: Pokemon, charizard: Pokemon) -> None:
        """Test that battle log is generated."""
        result = execute_battle(pikachu, charizard)
        assert len(result.battle_log) > 0
        assert "BATTLE:" in result.battle_log
        assert "pikachu" in result.battle_log.lower()
        assert "charizard" in result.battle_log.lower()

    def test_type_advantage_affects_outcome(
        self,
        charizard: Pokemon,
        blastoise: Pokemon,
    ) -> None:
        """Test that type advantage affects battle outcome."""
        # Blastoise (Water) should beat Charizard (Fire/Flying) due to type advantage
        result = execute_battle(charizard, blastoise)
        # Water is super effective against Fire
        assert result.pokemon2_score > result.pokemon1_score or result.is_draw
        if not result.is_draw:
            assert result.winner == blastoise

    def test_battle_symmetric_opponents(self, pikachu: Pokemon) -> None:
        """Test battle with identical Pokemon creates a draw."""
        pikachu2 = Pokemon(
            id=2,
            pokeapi_id=25,
            name="pikachu2",
            hp=pikachu.hp,
            attack=pikachu.attack,
            defense=pikachu.defense,
            special_attack=pikachu.special_attack,
            special_defense=pikachu.special_defense,
            speed=pikachu.speed,
            types=pikachu.types,
        )
        result = execute_battle(pikachu, pikachu2)
        # Same stats should result in a draw
        assert result.is_draw
        assert result.winner is None
