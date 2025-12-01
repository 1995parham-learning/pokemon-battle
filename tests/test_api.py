"""Tests for REST API endpoints."""

from httpx import AsyncClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health check returns healthy status."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPokemonEndpoints:
    """Tests for Pokemon endpoints."""

    async def test_get_pokemon_success(self, client: AsyncClient) -> None:
        """Test getting a Pokemon successfully."""
        response = await client.get("/api/v1/pokemon/pikachu")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "pikachu"
        assert data["pokeapi_id"] == 25
        assert data["hp"] == 35
        assert data["types"] == "electric"

    async def test_get_pokemon_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent Pokemon."""
        response = await client.get("/api/v1/pokemon/fakemon")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_get_pokemon_case_insensitive(self, client: AsyncClient) -> None:
        """Test that Pokemon names are case insensitive."""
        response = await client.get("/api/v1/pokemon/PIKACHU")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "pikachu"

    async def test_list_pokemon_empty(self, client: AsyncClient) -> None:
        """Test listing Pokemon when none exist."""
        response = await client.get("/api/v1/pokemon")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_pokemon_after_fetch(self, client: AsyncClient) -> None:
        """Test listing Pokemon after fetching some."""
        # First fetch a Pokemon
        await client.get("/api/v1/pokemon/pikachu")

        # Then list
        response = await client.get("/api/v1/pokemon")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["name"] == "pikachu" for p in data)


class TestBattleEndpoints:
    """Tests for battle endpoints."""

    async def test_create_battle_success(self, client: AsyncClient) -> None:
        """Test creating a battle successfully."""
        response = await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "pikachu", "pokemon2_name": "charizard"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["pokemon1"]["name"] == "pikachu"
        assert data["pokemon2"]["name"] == "charizard"
        assert "winner" in data
        assert data["pokemon1_score"] > 0
        assert data["pokemon2_score"] > 0
        assert "battle_log" in data

    async def test_create_battle_same_pokemon(self, client: AsyncClient) -> None:
        """Test that battling same Pokemon returns error."""
        response = await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "pikachu", "pokemon2_name": "pikachu"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "itself" in data["detail"].lower()

    async def test_create_battle_pokemon_not_found(self, client: AsyncClient) -> None:
        """Test battle with non-existent Pokemon."""
        response = await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "pikachu", "pokemon2_name": "fakemon"},
        )
        assert response.status_code == 404

    async def test_get_battle_success(self, client: AsyncClient) -> None:
        """Test getting a battle by ID."""
        # First create a battle
        create_response = await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "pikachu", "pokemon2_name": "charizard"},
        )
        battle_id = create_response.json()["id"]

        # Then get it
        response = await client.get(f"/api/v1/battles/{battle_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == battle_id

    async def test_get_battle_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent battle."""
        response = await client.get("/api/v1/battles/9999")
        assert response.status_code == 404

    async def test_list_battles(self, client: AsyncClient) -> None:
        """Test listing battles."""
        # Create a battle first
        await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "pikachu", "pokemon2_name": "charizard"},
        )

        response = await client.get("/api/v1/battles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_battle_type_advantage(self, client: AsyncClient) -> None:
        """Test that type advantage affects battle outcome."""
        # Blastoise (Water) vs Charizard (Fire/Flying)
        response = await client.post(
            "/api/v1/battles",
            json={"pokemon1_name": "charizard", "pokemon2_name": "blastoise"},
        )
        assert response.status_code == 201
        data = response.json()
        # Water should be super effective against Fire
        # Blastoise should have higher score or win
        if data["winner"]:
            assert data["winner"]["name"] == "blastoise"


class TestRootEndpoint:
    """Tests for root endpoint."""

    async def test_root(self, client: AsyncClient) -> None:
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
