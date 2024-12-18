import os
from flask import Flask, render_template, request, send_from_directory
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():

    conn = sqlite3.connect('games.db')
    cursor = conn.cursor()

    # Récupération des filtres de recherche
    search_query = request.args.get('search', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')

    query = "SELECT * FROM games WHERE 1=1"
    params = []

    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")

    if min_price:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    cursor.execute(query, params)
    games = cursor.fetchall()

    # Calcul des pages pour la pagination
    page = int(request.args.get('page', 1))
    total_games = len(games)


    games_per_page = 60



    total_pages = (total_games // games_per_page) + (1 if total_games % games_per_page else 0)
    games = games[(page-1)*games_per_page : page*games_per_page]

    conn.close()

    return render_template('index.html', games=games, page=page, total_pages=total_pages)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == '__main__':
    app.run(debug=True)
