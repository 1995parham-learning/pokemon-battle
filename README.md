**Pokémon Battle - Due Date:** 2 days

## Description

Develop an application that simulates a battle between two Pokémon. The
application takes two Pokémon names as input and determines the winner.
The application must fetch Pokémon data from pokeapi.co, persist battle
data, and expose functionalities through a REST API. This is a
backend-only exercise.

## Requirements

- **REST API:** Expose functionalities through REST API.
- **Backend Language:** The preferred language is Python.
- **Data Persistence:** Utilize a relational database (e.g.,
  PostgreSQL) to store information related to Pokémon and battle
  results. Design a suitable database schema
- **Battle Algorithm:** Develop a proper algorithm to determine the
  winner, and document it in the README file.
- **Error Handling:** Implement comprehensive error handling
- **Dockerization:** The entire application, including the database,
  must be containerized using Docker Compose.
- **Unit Testing:** Unit testing is required.
- **Documentation:**
  - **README:** The repository must include a comprehensive README
    file that provides:
    - Installation instructions for setting up the application
      locally.
    - Explanation of the battle algorithm, including the rationale
      behind the chosen approach.
    - Details on API endpoints and expected input/output formats.
- **Data Source:** Utilize the PokeAPI (pokeapi.co) to fetch Pokémon
  data. Assume it is a reliable external service.
  **Nice to Have:**
- **Caching:** Implement a caching mechanism to optimize performance
  when fetching Pokémon data from pokeapi.co.

**Tip:**

Regarding the battle algorithm, the `stat.change` field might be useful.
