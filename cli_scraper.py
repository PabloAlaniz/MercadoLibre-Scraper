"""Command-line interface for the MercadoLibre Scraper."""
from container import Container


def main():
    services = Container.create_for_cli()
    domain = input("País (ar/mx/br): ").strip() or "ar"
    product = input("Producto: ").strip()
    if not product:
        print("Debe ingresar un producto.")
        return

    try:
        limit = int(input("Límite (default 100): ").strip() or "100")
    except ValueError:
        limit = 100

    results = services.search_products.execute(domain, product, limit)
    print(f"Se encontraron {len(results)} productos.")


if __name__ == "__main__":
    main()
