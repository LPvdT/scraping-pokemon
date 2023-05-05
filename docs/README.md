# README

Scraping [Pokémon Database](https://pokemondb.net/) using the *Playwright* library combined with asynchronous *Python*.

# Todo

## Pokédex detail page

> [Example *Bulbasaur*](https://pokemondb.net/pokedex/bulbasaur)

- [ ] Type defenses
- [ ] Evolution chart
- [ ] *Bulbasaur*changes
- [ ] Name origin
- [ ] Moves learned by *Bulbasaur*: Requires another loop; lot of work

## Data dumps

- [ ] Find a way to properly tie the data together.
  - Such that everything is properly grouped by e.g. Pokémon.

# Bugs

## Pokédex detail page

> [Example *Pikachu*](https://pokemondb.net/pokedex/pikachu)

- [ ] Data below the table *Base stats* does not get scraped.
  - Suggestion: Find tables in relation to position of the header (e.g. *Base stats*), in order to properly determine its location.

## Concurrent Pokémon details

- [ ] Fix timeout issue
  - Currently, the `asyncio.gather` call for the Pokémon detail concurrent batch scraping causes a timeout.
