"""
MercadoLibre-specific enums.

These are retailer-specific and do not belong in the shared domain layer.
"""
from enum import Enum


class ProductCategory(str, Enum):
    """Product category detected from MercadoLibre listing pages."""
    CAR = 'car'
    PROPERTY = 'property'
    OTHERS = 'others'


class CountryDomain(str, Enum):
    """Country domain codes for MercadoLibre sites."""
    AR = 'ar'
    BO = 'bo'
    BR = 'br'
    CL = 'cl'
    CO = 'co'
    CR = 'cr'
    DO = 'do'
    EC = 'ec'
    GT = 'gt'
    HN = 'hn'
    MX = 'mx'
    NI = 'ni'
    PA = 'pa'
    PY = 'py'
    PE = 'pe'
    SV = 'sv'
    UY = 'uy'
    VE = 've'
