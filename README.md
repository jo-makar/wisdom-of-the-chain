# wisdom-of-the-chain

[Wisdom of the Crowd](https://en.wikipedia.org/wiki/Wisdom_of_the_crowd) applied to options chains

Scrape the option chain data:
- To be run every market day (via the crontab schedule: `0 18 * * 1-5`)
  - With the hour chosen to be sufficiently after market close (dependent on timezone)
- With a timeout of five hours (via the command `timeout 5h`); each ticker typically takes three minutes to download
  - Tickers may be specified via an .env file or directly on the command line (`-e TICKERS=...`)
- With an post-execution email of the container logs
```
0 18 * * 1-5 cd ~/projects/wisdom-of-the-chain; timeout 5h docker compose run --build scraper-yahoo-finance 2>&1 | tee scraper.log; [ -f mail.json ] && ./mail.py <scraper.log
```
