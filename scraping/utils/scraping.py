import requests
import pprint
import json
from datetime import datetime

def buscar_livro_por_nome(nome_livro):
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{nome_livro}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"erro": "Erro na requisição"}

    data = response.json()

    if "items" not in data:
        return {"erro": "Livro não encontrado"}

    books = []

    for item in data["items"]:
        volume_info = item["volumeInfo"]
        books.append({
            "title": volume_info.get("title"),
            "author": volume_info.get("authors", []),
            "editora": volume_info.get("publisher"),
            "year_published": parse_google_books_date(volume_info.get("publishedDate")),
            "short_description": volume_info.get("description"),
            "isbn_10": next((id['identifier'] for id in volume_info.get("industryIdentifiers", []) if id['type'] == 'ISBN_10'), None),
            "gtin_ean": next((id['identifier'] for id in volume_info.get("industryIdentifiers", []) if id['type'] == 'ISBN_13'), None),
            "pages_of_number": volume_info.get("pageCount"),
            "product_category": volume_info.get("categories", []),
            "idioma": volume_info.get("language"),
            "url_external_images": volume_info.get("imageLinks", {}).get("thumbnail")
        })

    return books





def parse_google_books_date(date_str):
    if not date_str:
        return None

    formats = '%Y-%m-%d'

    try:
        if datetime.strptime(date_str, formats).date():
            return date_str
    except ValueError:
        print(date_str)
        return None
