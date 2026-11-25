[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Bungsuu11jore7/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Bungsuu11jore7/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# THE WORLD TODAY — 24 November 2026

A dense one-page newspaper summing up Tuesday 24 November 2026 in 30 verified
stories across 9 regions: the Gaza strike that killed Hamas security chief
Naeem Abu Nahel leads the page with an illustrated scene, followed by the
record TAIEX surge (+8.99% to 40,122.35), the Shanghai party-boss purge, the
Zaporizhzhia strike (illustrated mid-page), the $41bn Sanofi–Insmed deal,
Huawei's US conviction, and Wall Street's AI reversal — every event dated
24 November 2026 and checked against Reuters, AP, UN and official sources.

## Run it

```bash
python3 main.py
```

Writes `entry.png` (768×1024) to `/output`, or to `$MAKEFUN_OUTPUT_DIR` when set.
Deterministic: two runs produce byte-identical output. Stdlib + Pillow only,
no network. `scene.png` (Gaza) and `scene2.png` (Zaporizhzhia) are loaded
from this directory at render time.
