## Bookmarks

### Thesis

- Include image from TA powerpoint on training model datapoipeline

### /model

- [] Define sudocode for agent interactons
- [] Make a mini version similar to a vcv rack wire connection.

### Data pipeline

- Make working baseline datafetcher for the websites listed below:
  - [ ] [OECD Data](https://data.oecd.org) – Data on economy, society, and environment from developed countries
  - [ ] [World Bank Open Data](https://data.worldbank.org) – Extensive economic and development data
  - [ ] [IMF Data](https://data.imf.org) – International Monetary Fund economic and financial data
  - [ ] [UNdata](https://data.un.org) – United Nations statistical databases
  - [ ] [Eurostat](https://ec.europa.eu/eurostat) – European Union statistics
  - [ ] [Trading Economics](https://tradingeconomics.com) – Macro indicators and forecasts _(limited free API usage)_
  - [ ] [Our World in Data](https://ourworldindata.org) – Global development, health, energy, and more
  - [ ] [Quandl / Open Financial Data Project](https://www.quandl.com) – Various financial and economic datasets _(many free)_
  - and store each in a sqlite .db file.

fetching data into file form single line command python3:

```python
import wbdata, sqlite3, pandas as pd; from datetime import datetime; wbdata.get_series("NY.GDP.PCAP.CD", country="all", date=(datetime(2010,1,1), datetime(2020,1,1)), freq='Y').reset_index().dropna().to_sql("gdp_per_capita", sqlite3.connect("gdp_per_capita.db"), if_exists="replace", index=False)
```

- Good resources for sqlite:
  - https://www.youtube.com/watch?v=8Xyn8R9eKB8 Bra video
  - /Users/lhh/Documents/LambdaTheSimulationProject/mainProject/ModelProject/DataPipeline/Collection
