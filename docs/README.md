# Work In Progress

Scraping [Pokémon Database](https://pokemondb.net/) using the *Playwright* library combined with asynchronous *Python*.

# Todo

## Pokédex detail page: `feature-scraper`

> [Example *Bulbasaur*](https://pokemondb.net/pokedex/bulbasaur)

- [ ] Type defenses
- [ ] Evolution chart
- [ ] *Bulbasaur* changes
- [ ] Name origin
- [ ] Moves learned by *Bulbasaur*: Requires another loop; lot of work

## Data dumps: `feature-scraper`

- [x] Find a way to properly tie the data together.
  - Such that everything is properly grouped by e.g. Pokémon.

## NOSQL database: `feature-db-nosql`

- [x] Create document table for Pokémon details.
  - [x] Insert data into it from the coroutines.
- [x] Create document tables for other document objects.

## Relational database: `feature-db-sql`

- [ ] Set up initial data models.
- [ ] Finish and validate the data models.
- [ ] Create CRUD methods in the classes.
- [ ] Insert data into the models from the coroutines.
- [ ] Optimize the models
  - [ ] Convert to proper data types, instead of using `TextField`.
  - [ ] Set appropriate contrains (`null`, `unique`, etc.)
  - [ ] Create appropriate indices for the tables.

# Bugs

## Pokédex detail page: `feature-scraper`

> [Example *Pikachu*](https://pokemondb.net/pokedex/pikachu)

- [ ] Data below the table *Base stats* does not get scraped.
  - This happens when the table does not occur in the expected `nth` position.
  - Suggestion: Find tables in relation to position of the header (e.g. *Base stats*), in order to properly determine its location.

## Concurrent Pokémon details: `feature-concurrent-details`

This branch still needs major work done.

- [ ] Fix timeout issue
  - Currently, the `asyncio.gather()` call for the Pokémon detail concurrent batch scraping causes a timeout.
