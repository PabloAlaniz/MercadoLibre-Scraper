"""
Domain entities for MercadoLibre Scraper.

These represent the core data structures of the application.
Each entity has to_dict() for serialization to plain dicts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProductListing:
    """A product from search results (listing page).

    Attributes:
        title: Product title.
        price: Price string (thousands separators already removed).
        post_link: URL to the product detail page.
        image_link: URL to the product image.
    """
    title: Optional[str] = None
    price: Optional[str] = None
    post_link: Optional[str] = None
    image_link: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dict."""
        return {
            'title': self.title,
            'price': self.price,
            'post_link': self.post_link,
            'image_link': self.image_link,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ProductListing:
        """Create from a dict."""
        return cls(
            title=data.get('title'),
            price=data.get('price'),
            post_link=data.get('post_link'),
            image_link=data.get('image_link'),
        )


@dataclass(frozen=True)
class ProductDetail:
    """Detailed product information from a product detail page.

    Attributes:
        title: Product title.
        price: Price string with currency symbol (e.g., "$ 1.500.000").
        publication_date: When the listing was published.
        author: Seller name.
        link: Markdown-formatted canonical URL.
        shipping: Shipping/delivery info.
        category: Product category string.
    """
    title: Optional[str] = None
    price: Optional[str] = None
    publication_date: Optional[str] = None
    author: Optional[str] = None
    link: Optional[str] = None
    shipping: Optional[str] = None
    category: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dict, omitting fields that are None."""
        result: dict = {}
        for key in ('title', 'price', 'publication_date', 'author', 'link', 'shipping'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> ProductDetail:
        """Create from a dict."""
        return cls(
            title=data.get('title'),
            price=data.get('price'),
            publication_date=data.get('publication_date'),
            author=data.get('author'),
            link=data.get('link'),
            shipping=data.get('shipping'),
            category=data.get('category'),
        )


@dataclass(frozen=True)
class CarProductDetail(ProductDetail):
    """Product detail for car listings.

    Attributes:
        year: Vehicle year.
        km: Kilometers string.
    """
    year: Optional[str] = None
    km: Optional[str] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.year is not None:
            result['year'] = self.year
        if self.km is not None:
            result['km'] = self.km
        return result

    @classmethod
    def from_dict(cls, data: dict) -> CarProductDetail:
        return cls(
            title=data.get('title'),
            price=data.get('price'),
            publication_date=data.get('publication_date'),
            author=data.get('author'),
            link=data.get('link'),
            shipping=data.get('shipping'),
            category=data.get('category'),
            year=data.get('year'),
            km=data.get('km'),
        )


@dataclass(frozen=True)
class PropertyProductDetail(ProductDetail):
    """Product detail for property/real estate listings.

    Attributes:
        m2: Square meters string.
    """
    m2: Optional[str] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.m2 is not None:
            result['m2'] = self.m2
        return result

    @classmethod
    def from_dict(cls, data: dict) -> PropertyProductDetail:
        return cls(
            title=data.get('title'),
            price=data.get('price'),
            publication_date=data.get('publication_date'),
            author=data.get('author'),
            link=data.get('link'),
            shipping=data.get('shipping'),
            category=data.get('category'),
            m2=data.get('m2'),
        )
