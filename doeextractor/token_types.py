import re

CITIES = [
    # mindanao
    "zamboanga city",
    "pagadian city",
    "dapitan city",
    "dipolog city",
    "isabela city",
    "cagayan de oro city",
    "el salvador city",
    "gingoog city",
    "balingasag",
    "villanueva",
    "opol",
    "tagoloan",
    "oroquieta city",
    "ozamiz city",
    "tangub city",
    "jimenez",
    "valencia city",
    "malaybalay city",
    "manolo fortich",
    "quezon",
    "iligan city",
    "mambajao / mahinog / catarman / sagay / jasaan",
    "davao city",
    "digos city",
    "panabo city",
    "samal city",
    "tagum city",
    "kapalong",
    "sto. tomas",
    "mati city",
    "nabunturan",
    "montevista",
    "general santos city",
    "koronadal city",
    "kidapawan city",
    "tacurong city",
    "bayugan city" "butuan city",
    "cabadbaran city",
    "bislig city",
    "tandag city",
    "surigao city",
    "siargao",
    "dinagat",
    "cotabato city",
]


def feature_is_city(text):
    try:
        return isinstance(CITIES.index(text.lower().strip()), int)
    except ValueError:
        return text.startswith("city of ") or text.endswith(" city")
    return False


BRANDS = [
    "petron",
    "shell",
    "caltex",
    "phoenix",
    "flying v",
    "seaoil",
    "jetti",
    "my gas",
    "independent",
]
# TODO: What to do with brands in headers?
HEADERS = [
    "product",
    "petron",
    "shell",
    "caltex",
    "phoenix",
    "flying v",
    "seaoil",
    "jetti",
    "my gas",
    "independent",
    "overall range",
    "common price",
    "average price",
]
SECONDARY_HEADERS = ["province", "cities", "liquid fuels price range"]
ALL_HEADERS = HEADERS + SECONDARY_HEADERS
UNCATEGORIZED = "uncategorized"
PRODUCT_TYPES = [
    "ron 100",
    "ron 97",
    "ron 95",
    "ron 91",
    "diesel",
    "diesel plus",
    "kerosene",
]
NONE_TYPES = [
    "no branch/outlet",
    "none",
    "-",
    "n.a",
]


PPriceRange = re.compile(r"(\d+\.\d+)\s\-\s(\d+\.\d+)")


def feature_is_price(text):
    try:
        return isinstance(float(text), float)
    except ValueError:
        return bool(re.match(PPriceRange, text))
    return False


# Register features
FEATURES = {
    "is_city": feature_is_city,
    "is_brand": lambda text: text.lower().strip() in BRANDS,
    "is_header": lambda text: text.lower().strip() in ALL_HEADERS,
    "is_product_type": lambda text: text.lower().strip() in PRODUCT_TYPES,
    "is_none_type": lambda text: len(text) == 0 or text.lower().strip() in NONE_TYPES,
    "is_price": feature_is_price,
}

TOKEN_TYPES = {
    "is_city": "city",
    "is_brand": "brand",
    "is_header": "header",
    "is_product_type": "product_type",
    "is_none_type": "none_type",
    "is_price": "price",
    "default": UNCATEGORIZED,
}
