# Blackjack Lab

>Work in progress. Take this readme with a grain of salt (for now...)


Blackjack Lab is a project designed to provide two core functionalities related to the game of Blackjack:  


## Play
- Play Blackjack sessions with or without additional (simulated) players, against a dealer.  
- Practice strategies or simply play for testing and experimentation (or for fun, of course).


## Simulate
- Run large-scale simulations of Blackjack sessions, with configurable numbers of players and rounds.  
- Define and test your own strategies under realistic conditions.
- Simulate Basic Strategy (proper noun indeed, not a basic strategy).
- Planned: Simulate Hi-Lo card-counting (builds off of Basic Strategy).
- Planned: Visualize data to better understand simulation results.  


### Notes for Blackjack Nerds:
- This project simulates each card and deck individually, mirroring the real-world.
- The shoe is modeled with a 6-deck capacity and a 75% penetration marker for realistic play.  
- Every game pays 3:2 for a Blackjack (natural 21).
- The above Blackjack conditions are preferable (or even necessary, most notably non-random cards) for card-counters to gain an edge.
- Optionally, a simulated Continuous Shuffle Machine can be enabled to remove all player advantage. This is a popular method used by casinos to discourage card counters.
