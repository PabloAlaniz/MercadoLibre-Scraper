# MercadoLibre Scraper 🛒

Web scraping tool for MercadoLibre with dual interface: interactive dashboard (Dash) and CLI. Supports 18 Latin American countries with specialized scrapers for products, cars, and real estate.

## ✨ Features

- **Multi-country support:** 18 LATAM countries (AR, MX, BR, CL, CO, etc.)
- **Dual interface:**
  - 🎨 Interactive web dashboard (Dash + Flask)
  - 💻 Command-line interface (CLI)
- **Specialized scrapers:**
  - General products
  - Cars (MLCar)
  - Real estate (MLProperties)
- **Data visualization:** Charts and tables in the dashboard
- **CSV export:** Structured data with configurable separator
- **Progress tracking:** tqdm progress bars
- **Logging:** Configurable logging system
- **Modular architecture:** Easy to extend with new scrapers

## 📋 Requirements

- Python 3.x
- Dependencies (install via `requirements.txt`):
  - `requests` - HTTP requests to MercadoLibre
  - `beautifulsoup4` - HTML parsing
  - `pandas` - DataFrame creation and manipulation
  - `matplotlib` - Data visualization
  - `dash` & `flask` - Web interface
  - `tqdm` - Progress bars
  - `dash-bootstrap-components` - UI components

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/PabloAlaniz/MercadoLibre-Scraper.git
cd MercadoLibre-Scraper
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
# Dashboard (web interface)
python main.py

# CLI (command-line)
python cli-scraper.py
```

## 💡 Usage

### Web Dashboard (Dash)

1. Start the dashboard:
```bash
python main.py
```

2. Open your browser and go to:
```
http://localhost:5003
```

3. **In the web interface:**
   - Select the country from the dropdown
   - Enter the product name
   - Set the maximum number of products to scrape
   - Click "Buscar" (Search)
   - View results in charts and tables

<p align="center"><img src="docs/home-v2.png"/></br>Dashboard Home</p>

### Command-Line Interface (CLI)

Run the CLI scraper:
```bash
python cli-scraper.py
```

**Follow the interactive prompts:**
```
Seleccioná el país:
1. Argentina
2. Bolivia
3. Brasil
...

Número de país (Ejemplo: 5): 1
Producto: notebook gamer
Cantidad máxima de productos a escrapear (por defecto: 1000): 50
```

Results will be saved to `data/[product_name].csv`

## 📁 Project Structure

```
MercadoLibre-Scraper/
├── main.py                    # Dashboard entry point
├── cli-scraper.py             # CLI entry point
├── dashboard.py               # Dash application setup
├── ui.py                      # UI components and layouts
├── callbacks.py               # Dash callbacks (interactivity)
├── scraper_manager.py         # Scraper orchestration
├── data_manager.py            # Data storage and retrieval
├── config.py                  # Configuration (URLs, ports, etc.)
├── log_config.py              # Logging configuration
├── utils.py                   # Helper functions
├── scrapers/
│   ├── base_scraper.py        # Abstract base scraper
│   └── mercadolibre/
│       ├── mercadolibre_scraper.py  # General products
│       ├── car_scraper.py           # MLCar specialized scraper
│       └── property_scraper.py      # Real estate scraper
├── data/                      # CSV output directory
├── docs/                      # Screenshots and documentation
└── templates/                 # Flask templates (if any)
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Server config
SERVER_CONFIG = {
    "debug": True,
    "port": 5003  # Change dashboard port
}

# Scraper config
SCRAPER_CONFIG = {
    'base_url': 'https://listado.mercadolibre.com.{domain}/',
    'page_increment': 50,
    'max_pages': 100  # Maximum pages to scrape
}

# Data config
DATA_DIRECTORY = "data"
CSV_SEPARATOR = ";"
```

## 🌎 Supported Countries

The scraper supports 18 Latin American countries:

| Code | Country        | Domain |
|------|----------------|--------|
| AR   | Argentina      | .ar    |
| BO   | Bolivia        | .bo    |
| BR   | Brasil         | .br    |
| CL   | Chile          | .cl    |
| CO   | Colombia       | .co    |
| CR   | Costa Rica     | .cr    |
| DO   | Rep. Dominicana| .do    |
| EC   | Ecuador        | .ec    |
| GT   | Guatemala      | .gt    |
| HN   | Honduras       | .hn    |
| MX   | México         | .mx    |
| NI   | Nicaragua      | .ni    |
| PA   | Panamá         | .pa    |
| PY   | Paraguay       | .py    |
| PE   | Perú           | .pe    |
| SV   | El Salvador    | .sv    |
| UY   | Uruguay        | .uy    |
| VE   | Venezuela      | .ve    |

## 📊 Data Export

Scraped data is saved to CSV files in the `data/` directory with the following structure:

```csv
title;price;link;location;...
"Notebook Gamer MSI";"150000";"https://...";"Capital Federal"
```

**Customize the CSV separator** in `config.py`:
```python
CSV_SEPARATOR = ","  # Use comma instead of semicolon
```

## 🧪 Development

### Adding a New Scraper

1. Create a new scraper class in `scrapers/mercadolibre/`:
```python
from scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def scrape_product_list(self, domain, product_name, limit):
        # Your scraping logic here
        pass
```

2. Register it in `scraper_manager.py`

### Running Tests

*(Tests not yet implemented)*

```bash
# When tests are added:
pytest tests/
```

## 🗺️ Roadmap

- [x] Agregar sort para el orden de los resultados
- [x] Scraper secundario que traiga info extra de cada producto
- [ ] Input para elegir la cantidad de páginas a escrapear
- [ ] Gráfico de barras con la distribución del precio
- [ ] Export to Excel (xlsx)
- [ ] Docker support
- [ ] API REST para scraping on-demand
- [ ] Scheduled scraping (cron jobs)
- [ ] Database storage (PostgreSQL/SQLite)
- [ ] Unit tests
- [ ] CI/CD pipeline

## 📝 Notes

- **Rate limiting:** Be respectful of MercadoLibre's servers. Use reasonable limits.
- **Robots.txt:** This scraper is for educational purposes. Check MercadoLibre's terms of service before large-scale scraping.
- **Data freshness:** MercadoLibre data changes frequently. For real-time accuracy, scrape regularly.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Author:** Pablo Alaniz  
**Inspired by:** [Original MercadoLibre scraper project](https://github.com/...)

