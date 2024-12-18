from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3
import os
import requests


# Initialiser la base de données SQLite
def init_db(db_name='games.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT,
            image_url TEXT,
            local_image_path TEXT,
            product_url TEXT,
            discount TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Sauvegarder les données dans SQLite
def save_games_to_db(game_infos, db_name='games.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for game in game_infos:
        cursor.execute('''
            INSERT INTO games (title, price, image_url, local_image_path, product_url, discount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (game['title'], game['price'], game['image_url'], game['local_image_path'], game['product_url'], game['discount']))
    conn.commit()
    conn.close()


# Télécharger une image et la sauvegarder localement
def download_image(image_url, save_dir='images'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_name = image_url.split("/")[-1].split("?")[0]
            save_path = os.path.join(save_dir, image_name)
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return save_path
        else:
            return None
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image : {e}")
        return None


# Extraire les informations des jeux
def extract_game_info(base_url, num_pages=-1):
    driver = webdriver.Chrome()
    game_infos = []
    page = 1

    while True:
        page_url = f"{base_url}&page={page}"
        driver.get(page_url)
        print(f"Scraping page {page}...")

        # Trouver les éléments de jeux
        game_elements = driver.find_elements(By.CLASS_NAME, 'item.force-badge')

        if not game_elements:
            print(f"Page {page} vide ou fin des résultats. Fin du scraping.")
            break

        for index, game_element in enumerate(game_elements, start=1):
            try:
                # Titre du jeu
                title = game_element.find_element(By.CLASS_NAME, "title").text

                # Prix
                price = game_element.find_element(By.CLASS_NAME, "price").text

                # URL de l'image
                image_element = game_element.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("data-src") or image_element.get_attribute("src")

                # Télécharger l'image
                local_image_path = download_image(image_url)

                # URL du produit
                product_url = game_element.find_element(By.CLASS_NAME, "cover").get_attribute("href")

                # Réduction
                discount_element = game_element.find_element(By.CLASS_NAME, "discount")
                discount = discount_element.text if discount_element else "No discount"

                game_info = {
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'local_image_path': local_image_path,
                    'product_url': product_url,
                    'discount': discount
                }

                game_infos.append(game_info)
                print(f"Page {page}, Jeu {index} : {title} extrait.")

            except Exception as e:
                print(f"Page {page}, Jeu {index} : erreur lors de l'extraction ({e}). Ignoré.")

        if num_pages != -1 and page >= num_pages:
            print("Nombre de pages spécifié atteint. Fin du scraping.")
            break

        page += 1

    driver.quit()
    return game_infos


# Initialiser la base de données
init_db()

# URL de base pour Instant Gaming
base_url = "https://www.instant-gaming.com/fr/rechercher/?platform%5B%5D=&type%5B%5D=steam&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=100&noprice=1&instock=1&gametype=all&search_tags=0&query="

# Définir le nombre de pages (-1 pour toutes les pages disponibles)
num_pages_to_scrape = 20

# Extraire les informations des jeux
game_infos = extract_game_info(base_url, num_pages_to_scrape)

# Sauvegarder les jeux dans la base de données
save_games_to_db(game_infos)

print("Scraping terminé. Données sauvegardées dans la base de données.")
