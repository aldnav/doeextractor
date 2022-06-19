import itertools
import statistics
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pprint import PrettyPrinter
from typing import List

from doeextractor.models.fuel_line_price import FuelLinePriceItem, FuelPrice

pp = PrettyPrinter(indent=2)
DECIMAL_PLACES = 2


def analyse(results: List[FuelLinePriceItem]):
    """Get mean, median, mode of prices from all companies"""
    company_products = defaultdict(lambda: defaultdict(list))
    for line_price_item in results:
        line_price_item = FuelLinePriceItem(**line_price_item)
        for fuel_price in line_price_item.prices:
            fuel_price = FuelPrice(**fuel_price)
            if not fuel_price.company:
                continue
            # price can be a range
            price_raw = set(fuel_price.price.replace("-", "").split(" ")) - {""}
            try:
                price = list(map(Decimal, (list(itertools.chain(price_raw)))))
            except InvalidOperation:
                continue
            if len(price) == 0:
                continue
            company_products[fuel_price.company][line_price_item.product].append(price)

    results = defaultdict(lambda: defaultdict(dict))
    for company in company_products.keys():
        for product, prices in company_products[company].items():
            flattened_prices = sorted(list(itertools.chain(*prices)))
            results[company][product]["mean"] = round(
                float(mean(flattened_prices)), DECIMAL_PLACES
            )
            results[company][product]["median"] = round(
                float(median(flattened_prices)), DECIMAL_PLACES
            )
            results[company][product]["mode"] = round(
                float(mode(flattened_prices)), DECIMAL_PLACES
            )
    return results


def mean(items):
    return statistics.mean(items)


def median(items):
    return statistics.median(items)


def mode(items):
    return statistics.mode(items)
