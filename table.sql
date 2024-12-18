CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price TEXT,
    image_url TEXT,
    local_image_path TEXT,
    product_url TEXT,
    discount TEXT
)