"""
Tests for the domain layer: enums, value objects, and entities.
"""
import pytest

from domain.enums import Currency
from domain.value_objects import Money, Kilometers, SquareMeters
from domain.entities import ProductListing, ProductDetail, CarProductDetail, PropertyProductDetail


class TestCurrency:
    """Tests for Currency enum."""

    def test_ars_value(self):
        assert Currency.ARS == 'ARS'

    def test_usd_value(self):
        assert Currency.USD == 'USD'


class TestMoney:
    """Tests for Money value object."""

    def test_convert_usd_to_ars(self):
        m = Money(amount=100, currency=Currency.USD)
        converted = m.convert_to(Currency.ARS, rate=1000.0)
        assert converted.amount == 100000.0
        assert converted.currency == Currency.ARS

    def test_convert_ars_to_usd(self):
        m = Money(amount=100000, currency=Currency.ARS)
        converted = m.convert_to(Currency.USD, rate=1000.0)
        assert converted.amount == 100
        assert converted.currency == Currency.USD

    def test_convert_same_currency_noop(self):
        m = Money(amount=100, currency=Currency.USD)
        converted = m.convert_to(Currency.USD, rate=1000.0)
        assert converted is m

    def test_is_immutable(self):
        m = Money(amount=100, currency=Currency.USD)
        with pytest.raises(AttributeError):
            m.amount = 200


class TestKilometers:
    """Tests for Kilometers value object."""

    def test_parse_standard_format(self):
        km = Kilometers.from_string("50.000 km")
        assert km is not None
        assert km.value == 50000

    def test_parse_large_value(self):
        km = Kilometers.from_string("150.000 km")
        assert km is not None
        assert km.value == 150000

    def test_parse_no_dots(self):
        km = Kilometers.from_string("5000 km")
        assert km is not None
        assert km.value == 5000

    def test_parse_none_returns_none(self):
        assert Kilometers.from_string(None) is None

    def test_parse_empty_string_returns_none(self):
        assert Kilometers.from_string("") is None

    def test_is_immutable(self):
        km = Kilometers(value=50000)
        with pytest.raises(AttributeError):
            km.value = 60000


class TestSquareMeters:
    """Tests for SquareMeters value object."""

    def test_parse_totales_format(self):
        m2 = SquareMeters.from_string("150 m² totales")
        assert m2 is not None
        assert m2.value == 150.0

    def test_parse_simple_format(self):
        m2 = SquareMeters.from_string("250 m²")
        assert m2 is not None
        assert m2.value == 250.0

    def test_parse_with_dots(self):
        m2 = SquareMeters.from_string("1.500 m² totales")
        assert m2 is not None
        assert m2.value == 1500.0

    def test_parse_none_returns_none(self):
        assert SquareMeters.from_string(None) is None

    def test_parse_empty_string_returns_none(self):
        assert SquareMeters.from_string("") is None

    def test_parse_no_m2_returns_none(self):
        assert SquareMeters.from_string("150 metros") is None

    def test_is_immutable(self):
        m2 = SquareMeters(value=150.0)
        with pytest.raises(AttributeError):
            m2.value = 200.0


class TestProductListing:
    """Tests for ProductListing entity."""

    def test_construction(self):
        listing = ProductListing(
            title='iPhone 15',
            price='1500000',
            post_link='https://example.com/iphone',
            image_link='https://example.com/img.jpg',
        )
        assert listing.title == 'iPhone 15'
        assert listing.price == '1500000'

    def test_to_dict(self):
        listing = ProductListing(
            title='iPhone 15',
            price='1500000',
            post_link='https://example.com/iphone',
            image_link='https://example.com/img.jpg',
        )
        d = listing.to_dict()
        assert d == {
            'title': 'iPhone 15',
            'price': '1500000',
            'post_link': 'https://example.com/iphone',
            'image_link': 'https://example.com/img.jpg',
        }

    def test_to_dict_uses_image_link_underscore(self):
        """Key must be 'image_link' (with underscore)."""
        listing = ProductListing(image_link='https://example.com/img.jpg')
        d = listing.to_dict()
        assert 'image_link' in d

    def test_from_dict(self):
        d = {
            'title': 'Test',
            'price': '100',
            'post_link': 'https://example.com',
            'image_link': 'https://example.com/img.jpg',
        }
        listing = ProductListing.from_dict(d)
        assert listing.image_link == 'https://example.com/img.jpg'

    def test_round_trip(self):
        original = ProductListing(
            title='Test Product',
            price='100000',
            post_link='https://example.com/product',
            image_link='https://example.com/img.jpg',
        )
        d = original.to_dict()
        restored = ProductListing.from_dict(d)
        assert restored.title == original.title
        assert restored.price == original.price
        assert restored.post_link == original.post_link
        assert restored.image_link == original.image_link

    def test_defaults_to_none(self):
        listing = ProductListing()
        d = listing.to_dict()
        assert d['title'] is None
        assert d['price'] is None


class TestProductDetail:
    """Tests for ProductDetail entity."""

    def test_construction_general_product(self):
        detail = ProductDetail(
            title='iPhone 15',
            price='$ 1.500.000',
            publication_date='Hace 2 dias',
            author='Apple Store',
            link='[Link](https://example.com)',
            shipping='Llega manana',
        )
        assert detail.title == 'iPhone 15'

    def test_to_dict_omits_none_fields(self):
        detail = ProductDetail(
            title='iPhone 15',
            price='$ 1.500.000',
        )
        d = detail.to_dict()
        assert 'title' in d
        assert 'price' in d
        assert 'shipping' not in d

    def test_to_dict_base_fields_match_scraper_output(self):
        detail = ProductDetail(
            title='iPhone 15',
            price='$ 500.000',
            publication_date='Hace 2 dias',
            author='Apple Store',
            link='[Link](https://test.com/iphone)',
            shipping='Llega manana',
        )
        d = detail.to_dict()
        expected_keys = {'title', 'price', 'publication_date', 'author', 'link', 'shipping'}
        assert set(d.keys()) == expected_keys

    def test_from_dict(self):
        d = {
            'title': 'Test',
            'shipping': 'Llega mañana',
            'category': 'others',
        }
        detail = ProductDetail.from_dict(d)
        assert detail.shipping == 'Llega mañana'
        assert detail.category == 'others'


class TestCarProductDetail:
    """Tests for CarProductDetail entity."""

    def test_construction(self):
        detail = CarProductDetail(
            title='Toyota Corolla',
            price='U$S 15.000',
            year='2020',
            km='50.000 km',
        )
        assert detail.year == '2020'
        assert detail.km == '50.000 km'

    def test_to_dict_includes_car_fields(self):
        detail = CarProductDetail(
            title='Toyota Corolla',
            price='U$S 15.000',
            year='2020',
            km='50.000 km',
        )
        d = detail.to_dict()
        assert d['year'] == '2020'
        assert d['km'] == '50.000 km'
        assert 'm2' not in d

    def test_to_dict_omits_none_car_fields(self):
        detail = CarProductDetail(title='Car')
        d = detail.to_dict()
        assert 'year' not in d
        assert 'km' not in d

    def test_inherits_from_product_detail(self):
        assert issubclass(CarProductDetail, ProductDetail)

    def test_from_dict(self):
        d = {'title': 'Corolla', 'year': '2020', 'km': '50k'}
        detail = CarProductDetail.from_dict(d)
        assert detail.year == '2020'

    def test_round_trip(self):
        original = CarProductDetail(
            title='Toyota Corolla',
            price='U$S 15.000',
            author='Seller',
            year='2020',
            km='50.000 km',
            category='car',
        )
        d = original.to_dict()
        restored = CarProductDetail.from_dict(d)
        assert restored.title == original.title
        assert restored.year == original.year
        assert restored.km == original.km


class TestPropertyProductDetail:
    """Tests for PropertyProductDetail entity."""

    def test_construction(self):
        detail = PropertyProductDetail(
            title='Departamento',
            price='U$S 100.000',
            m2='150 m² totales',
        )
        assert detail.m2 == '150 m² totales'

    def test_to_dict_includes_property_fields(self):
        detail = PropertyProductDetail(
            title='Departamento',
            price='U$S 100.000',
            m2='150 m² totales',
        )
        d = detail.to_dict()
        assert d['m2'] == '150 m² totales'
        assert 'year' not in d
        assert 'km' not in d

    def test_to_dict_omits_none_m2(self):
        detail = PropertyProductDetail(title='Prop')
        d = detail.to_dict()
        assert 'm2' not in d

    def test_inherits_from_product_detail(self):
        assert issubclass(PropertyProductDetail, ProductDetail)

    def test_from_dict(self):
        d = {'title': 'Depto', 'm2': '150 m²'}
        detail = PropertyProductDetail.from_dict(d)
        assert detail.m2 == '150 m²'
