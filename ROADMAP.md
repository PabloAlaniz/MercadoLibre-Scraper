# Roadmap — MercadoLibre Scraper

> Última actualización: 2026-02-19

## ✅ Implementado

### Core
- **Clean Architecture** — Dominio, aplicación, infraestructura y presentación desacoplados
- **Multi-país** — 18 países de LATAM soportados (AR, MX, BR, CL, CO, etc.)
- **Interfaz dual** — Dashboard web (Dash) + CLI

### Scrapers
- **MercadoLibreScraper** — Productos generales con paginación
- **CarScraper** — Especializado para autos (km, año, motor)
- **PropertyScraper** — Especializado para inmuebles (m², ambientes)

### Dominio
- **Entidades** — `ProductListing`, `ProductDetail`, `CarProductDetail`, `PropertyProductDetail`
- **Value Objects** — `Money`, `Kilometers`, `SquareMeters` con parsing y conversión
- **Ports** — Interfaces para scrapers, exportadores, notificadores, exchange rates

### Infraestructura
- **CsvExporter** — Exportación a CSV con separador configurable
- **DolarApiExchangeRate** — Conversión USD ↔ ARS via DolarAPI
- **SocketIOProgressNotifier** — Notificaciones en tiempo real al dashboard
- **NullProgressNotifier** — Para CLI y tests

### Presentación
- **Dashboard Dash** — UI interactiva con gráficos y tablas
- **Selector de país** — Dropdown con 18 países
- **Progreso en tiempo real** — Via Flask-SocketIO

### Quality
- **127 tests unitarios** — Cobertura de domain, application, infrastructure, presentation
- **23 tests de integración** — Requests reales a MercadoLibre
- **CI/CD** — GitHub Actions ejecuta tests en cada push/PR

## 🚧 En progreso

*(nada actualmente)*

## 📋 Backlog

### Corto plazo (v1.x)
- [ ] **Input páginas** — Permitir al usuario elegir cantidad de páginas a scrapear
- [ ] **Gráfico distribución de precios** — Histograma de precios en el dashboard
- [ ] **Export Excel** — Exportación a .xlsx además de CSV

### Mediano plazo (v2.x)
- [ ] **Docker support** — Dockerfile + docker-compose para deploy fácil
- [ ] **API REST** — Endpoints para scraping on-demand (FastAPI)
- [ ] **Scheduled scraping** — Cron jobs para monitoreo periódico
- [ ] **Base de datos** — PostgreSQL o SQLite para persistir resultados

### Arquitectura (ya preparado)
- [ ] **Nuevo retailer** — Agregar scrapers para Amazon, eBay, etc. (Container ya soporta multi-retailer)

## 💡 Ideas

- **Rate limiting inteligente** — Backoff automático cuando se detecta throttling
- **Proxy/Tor support** — Rotación de IPs para scraping masivo
- **Historización de precios** — Tracking de precio en el tiempo (requiere DB)
- **Alertas de precio** — Notificar cuando un producto baja de cierto umbral
- **Comparador** — Comparar precios del mismo producto entre países
- **Export BigQuery** — Integración directa para análisis de datos
- **Playwright mode** — Scraping de páginas con JS rendering (ya existe `playwright_client.py`)

---
*Generado por Brújula 🧭*
