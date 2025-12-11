import json

sample_products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 99.99,
        "quantity": 50,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "description": "Fitness tracker with heart rate monitor",
        "price": 149.99,
        "quantity": 30,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"
    },
    {
        "id": 3,
        "name": "Python Programming Book",
        "description": "Complete guide to Python programming",
        "price": 39.99,
        "quantity": 100,
        "category": "Books",
        "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400"
    }
]

with open('products.json', 'w') as f:
    json.dump(sample_products, f, indent=4)

print("Sample products added to products.json")