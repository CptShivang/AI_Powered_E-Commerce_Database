import os
from PIL import Image
import MySQLdb
from dotenv import load_dotenv

load_dotenv()

# Database connection
db = MySQLdb.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    passwd=os.getenv('MYSQL_PASSWORD'),
    db=os.getenv('MYSQL_DB')
)

cur = db.cursor()

image_dir = 'static/images'
thumb_dir = os.path.join(image_dir, 'thumbnails')
os.makedirs(thumb_dir, exist_ok=True)

# Fetch products that are missing thumbnails
cur.execute("SELECT product_id, image_url FROM products WHERE thumb_url IS NULL OR thumb_url = ''")
rows = cur.fetchall()

for product_id, image_filename in rows:
    image_path = os.path.join(image_dir, image_filename)
    thumb_path = os.path.join(thumb_dir, image_filename)

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        continue

    try:
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        img.save(thumb_path)

        cur.execute("UPDATE products SET thumb_url = %s WHERE product_id = %s", (f'thumbnails/{image_filename}', product_id))
        db.commit()
        print(f"Thumbnail created for product {product_id}")
    except Exception as e:
        print(f"Failed for {image_filename}: {e}")

cur.close()
db.close()
