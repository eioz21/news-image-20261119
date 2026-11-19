# news-image-20261119

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/eioz21/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/eioz21/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

One image summing up the world's news of Thursday 19 November 2026,
for the make.fun bounty of the same name.

## How it works

`main.py` (Python 3.13, standard library only) draws a newspaper
front page — 1024 x 1024 — and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output`). Everything is drawn in code: a hand-written 5x7
bitmap font, simple shape primitives, and a hand-rolled PNG encoder
built on `zlib`. No network, no files read, no randomness, so two runs
write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The day's stories (all reported 19 November 2026)

- **Lead — Shenzhen:** Trump, Xi and Putin hold their first three-way
  summit, on the sidelines of the APEC forum.
- **Middle East:** Iran widens attacks on Gulf states (Bahrain, Kuwait)
  after US forces hit a missile site on Qeshm Island.
- **Ukraine:** Ukraine strikes the Crimean Bridge for a third time in
  a week, as peace talks continue in Abu Dhabi.
- **Markets:** Anthropic debuts on Nasdaq as ANT after pricing the
  largest IPO ever at $81.3bn.
- **Justice:** The ICJ prepares its verdict on genocide claims against
  Myanmar over the Rohingya.
- **Space:** NASA's Voyager 1 reaches one light-day from Earth,
  50 years after launch.
- **Also today:** GTA VI rolls out worldwide; Hakeem Jeffries is
  nominated for US House Speaker; the EU backs the Indonesia trade deal.
