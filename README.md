[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Bungsuu11jore7/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Bungsuu11jore7/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# THE WORLD TODAY — 24 November 2026

A dense one-page newspaper summing up Tuesday 24 November 2026 in 38 verified
stories across 7 regions and 19 fields: the Shanghai party-boss purge, Huawei's
US conviction (10 of 12 counts), Russian attacks killing 9 across Ukraine, the
Solomons letting its China pact lapse, Senegal's restored AFCON title, the Dow
closing back above 50,000, the $41bn Sanofi–Insmed deal, the Gaza strike that
killed Hamas security chief Naeem Abu Nahel, and 30 more — every event dated
24 November 2026, sourced by name (Reuters, AP, AFP, official releases), with
claim badges (C = 2+ outlets, O = official, R = one outlet, CL = one side's
claim), a UTC timeline, an IN NUMBERS strip, and a world map with numbered pins
for the 13 drawn feature stories.

## Run it

```bash
python3 main.py
```

Writes `entry.png` (1024×1024) to `/output`, or to a temp directory when
`/output` is not writable. Deterministic: two runs produce byte-identical
output. Stdlib + Pillow only, no network. `card1.png`–`card13.png` (original
drawn scenes, no photos) are loaded from this directory at render time.
