import requests
from bs4 import BeautifulSoup
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def retry_request(func):
    def wrapper(*args, **kwargs):
        max_retries = 40
        for attempt in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise e
                wait_time = random.uniform(1, 5)
                print(f"Reintentando ({attempt}/10)... Esperando {wait_time:.2f} segundos.")
                time.sleep(wait_time)
    return wrapper

@retry_request
def get_price(url: str) -> str:
    """
    Extrae el precio de un producto en Amazon a partir de su URL.

    Args:
        url (str): URL de la página del producto.

    Returns:
        str: El precio del producto como texto. Si no se encuentra, devuelve un mensaje de error.
    """
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Extraer la parte entera y fraccionaria del precio
    whole_price = soup.select_one("span.a-price-whole")
    fractional_price = soup.select_one("span.a-price-fraction")
    print(whole_price, fractional_price)

    if whole_price and fractional_price:
        # Limpiar los datos y combinar las partes del precio
        price_whole = whole_price.text.strip().replace(",", "")
        price_fraction = fractional_price.text.strip()
        price = f"{price_whole},{price_fraction} €"
        return price

    return "No se pudo encontrar el precio en esta página."

@retry_request
def get_product_info(url: str) -> tuple:
    """
    Extrae el nombre y el precio de un producto de Amazon.

    Args:
        url (str): URL de la página del producto.

    Returns:
        tuple: (nombre del producto, precio del producto). Si no se encuentra, devuelve mensajes de error.
    """
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    # Extraer nombre del producto
    title_element = soup.find("span", id="productTitle")
    product_name = title_element.text.strip() if title_element else None

    # Extraer el precio del producto
    whole_price = soup.select_one("span.a-price-whole")
    fractional_price = soup.select_one("span.a-price-fraction")

    if whole_price and fractional_price:
        price = f"{whole_price.text.strip().replace(',', '')},{fractional_price.text.strip()} €"
    else:
        price = None

    # Validar que se obtuvo el nombre y el precio
    if not product_name:
        product_name = "Nombre no disponible"
    if not price:
        price = "Precio no disponible"

    return product_name, price
