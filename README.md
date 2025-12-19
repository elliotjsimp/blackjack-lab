# Blackjack Lab

>Work in progress. Specifically, I am having trouble finding the right betting scheme to maximize max growth, while minimizing risk of ruin. If you are a Blackjack and/or math person and stumble upon this repo, please let me know how to fix it! I will probably fix it eventually but the opportunity cost is not favourable at this time.


### Notes for Blackjack Nerds:
- This project simulates each card and deck individually, mirroring the real-world.
- The shoe is modeled with a 6-deck capacity and a 75% penetration marker for realistic play.  
- Every game pays 3:2 for a Blackjack (natural 21).
- The above Blackjack conditions are preferable (or even necessary, most notably non-random cards) for card-counters to gain an edge.
- Optionally, a simulated Continuous Shuffle Machine can be enabled to remove all player advantage. This is a popular method used by casinos to discourage card counters.


### Note on implementation:
I am not thoroughly pleased with my implementation. I did not know how to play Blackjack when I started making this project (which is pretty funny, I think), and there were more rules than I had realised. This means that over time, the codebase has became somewhat Frankenstein-ish. A good lesson learned for me: plan, plan and then plan some more!
