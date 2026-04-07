# FODA — MercadoLibre Scraper

**Fecha:** 2026-03-25  
**Versión analizada:** 1.x (post Clean Architecture refactor)  
**Repositorio:** PabloAlaniz/MercadoLibre-Scraper

---

## 🟢 Fortalezas

### Arquitectura
- **Clean Architecture completa** — Dominio, aplicación, infraestructura y presentación desacoplados
- **Container pattern** — Composition root centralizado, fácil de extender a nuevos retailers
- **Duck typing via Protocol** — Ports definidos sin dependencias de implementación
- **Value Objects** — `Money`, `Kilometers`, `SquareMeters` con parsing y conversión robustos

### Funcionalidad
- **Multi-país nativo** — 18 países de LATAM soportados
- **Scrapers especializados** — Productos generales, autos (`CarScraper`), inmuebles (`PropertyScraper`)
- **Interfaz dual** — Dashboard web interactivo (Dash) + CLI para automatización
- **Conversión de moneda** — USD ↔ ARS via DolarAPI integrado
- **Tiempo real** — SocketIO para progreso de scraping en dashboard

### Calidad
- **150 tests** (127 unit + 23 integration) — Cobertura sólida
- **CI/CD** — GitHub Actions ejecutando tests en cada push
- **Coverage reporting** — Workflow para reportar cobertura (83%)
- **MIT License** — Open source, fácil de contribuir

### Documentación
- **README completo** — Instalación, uso, arquitectura, troubleshooting
- **Roadmap documentado** — En `docs/roadmap.md`
- **Screenshots** — Dashboard con visualización de datos

---

## 🔴 Debilidades

### Técnicas
- **Sin persistencia** — Solo exporta a CSV, no guarda en DB
- **Sin rate limiting inteligente** — Puede ser bloqueado por MercadoLibre
- **Parsing frágil** — Cambios en HTML de ML rompen el scraper
- **No JS rendering** — `playwright_client.py` existe pero no está integrado

### UX
- **Dashboard anticuado** — Dash/Flask vs frameworks modernos (Next.js, Streamlit)
- **Sin autenticación** — Cualquiera puede usar el dashboard
- **Sin API REST** — No se puede consumir programáticamente
- **Sin Docker** — Requiere setup manual de Python

### Mantenimiento
- **3 stars en GitHub** — Baja visibilidad
- **Código legacy parcial** — Algunos archivos pre-refactor (`utils.py`)
- **Dependencias desactualizadas** — Dash, Flask-SocketIO

### Limitaciones de Producto
- **Solo MercadoLibre** — No soporta otros marketplaces aún
- **Sin historización** — No trackea precios en el tiempo
- **Sin alertas** — No notifica cambios de precio

---

## 🟡 Oportunidades

### Mercado
- **E-commerce analytics en auge** — Demanda creciente de herramientas de pricing
- **Dropshipping/arbitraje** — Casos de uso claros para comparación de precios
- **LATAM underserved** — Pocas herramientas de scraping específicas para la región

### Expansión de Features
- **API REST (FastAPI)** — Scraping on-demand para integraciones
- **Base de datos** — PostgreSQL para historización y análisis
- **Docker/Cloud** — Deploy en Cloud Run, fácil de escalar
- **Playwright mode** — Soporte para páginas con JS rendering

### Nuevos Retailers
- **Amazon** — Reutilizar arquitectura, solo nuevo scraper
- **eBay** — Similar a Amazon
- **Retailers locales** — Frávega, Garbarino (Argentina)

### Modelo de Negocio
- **SaaS de pricing intelligence** — Cobrar por queries o suscripción
- **API as a service** — Endpoints pagos con rate limits
- **White-label** — Vender a retailers que quieren monitorear competencia

---

## 🔵 Amenazas

### Técnicas
- **MercadoLibre anti-scraping** — Captchas, rate limiting, bloqueos de IP
- **Cambios de HTML** — Cualquier rediseño de ML rompe los selectores
- **Cloudflare/Bot detection** — Cada vez más sofisticado

### Legales
- **ToS de MercadoLibre** — El scraping puede violar términos de servicio
- **Legislación de datos** — Regulaciones que podrían afectar scraping

### Competencia
- **Herramientas comerciales** — Keepa, CamelCamelCamel (Amazon), más maduras
- **APIs oficiales** — Si MercadoLibre abre API de precios, el scraper pierde valor
- **AI-powered scrapers** — Herramientas que usan LLMs para adaptarse a cambios de HTML

### Riesgos de Proyecto
- **Mantenimiento a largo plazo** — Sin revenue, difícil de sostener
- **Dependencias abandonadas** — Dash no es tan activo como antes
- **Single maintainer** — Sin comunidad activa de contributors

---

## 📊 Resumen Ejecutivo

| Dimensión | Score | Justificación |
|-----------|-------|---------------|
| Fortalezas | ⭐⭐⭐⭐ | Arquitectura sólida, 150 tests, multi-país |
| Debilidades | ⭐⭐⭐ | Sin DB, sin Docker, dashboard anticuado |
| Oportunidades | ⭐⭐⭐⭐ | Mercado creciente, expansión a otros retailers |
| Amenazas | ⭐⭐⭐ | Anti-scraping de ML, competencia comercial |

### Recomendaciones Prioritarias

1. **Docker + Cloud Run** — Facilita deployment y pruebas
2. **API REST (FastAPI)** — Habilita integraciones y posible monetización
3. **PostgreSQL** — Persistencia para historización y análisis
4. **Playwright integration** — Resiliencia ante páginas con JS rendering

### Próximos Pasos Sugeridos

| Prioridad | Feature | Esfuerzo | Impacto |
|-----------|---------|----------|---------|
| 🔴 Alta | Docker support | Bajo | Alto |
| 🔴 Alta | API REST básica | Medio | Alto |
| 🟡 Media | PostgreSQL integration | Medio | Medio |
| 🟡 Media | Historización de precios | Medio | Alto |
| 🟢 Baja | Nuevo retailer (Amazon) | Alto | Medio |

---

*Análisis generado por Margarita — 25 marzo 2026*
