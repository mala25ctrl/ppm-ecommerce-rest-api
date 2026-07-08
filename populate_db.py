import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from store.models import OrderItem, Order, CartItem, Cart, Product, Category

User = get_user_model()


def run():
    print("Pulizia database...")
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    CartItem.objects.all().delete()
    Cart.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()

    print("Creazione utenti...")
    admin = User.objects.create_user(
        username='admin_demo',
        password='admin12345',
        email='admin@demo.com',
        role='ADMIN'
    )
    manager = User.objects.create_user(
        username='manager_demo',
        password='manager12345',
        email='manager@demo.com',
        role='MANAGER'
    )
    customer1 = User.objects.create_user(
        username='customer_demo',
        password='customer12345',
        email='customer@demo.com',
        role='CUSTOMER'
    )
    customer2 = User.objects.create_user(
        username='mario_rossi',
        password='mario12345',
        email='mario@demo.com',
        role='CUSTOMER'
    )

    print("Creazione categorie...")
    electronics = Category.objects.create(name='Elettronica', slug='elettronica')
    clothing = Category.objects.create(name='Abbigliamento', slug='abbigliamento')
    books = Category.objects.create(name='Libri', slug='libri')

    print("Creazione prodotti...")
    laptop = Product.objects.create(
        name='Laptop Pro 15',
        description='Potente laptop con 16GB Ram e 512GB SSD.',
        price=1299.99,
        stock=15,
        category=electronics,
    )
    smartphone = Product.objects.create(
        name='Smartphone X12',
        description='Ultimo smartphone X12 con connessione 5G',
        price=800,
        stock=30,
        category=electronics,
    )
    headphones = Product.objects.create(
        name='Auricolari Wireless',
        description='Auricolari wireless con cancellazione del rumore.',
        price=199.99,
        stock=50,
        category=electronics
    )
    tshirt = Product.objects.create(
        name='Cotton T-Shirt',
        description='Comoda T-shirt ',
        price=19.99,
        stock=100,
        category=clothing
    )
    jacket = Product.objects.create(
        name='Giacca invernale',
        description='Giacca invernale calda con rivestimento impermeabile.',
        price=89.99,
        stock=25,
        category=clothing
    )
    python_book = Product.objects.create(
        name='Programmazione Python',
        description='Guida completa alla programmazione in Python.',
        price=39.99,
        stock=40,
        category=books
    )
    django_book = Product.objects.create(
        name='Django REST Framework',
        description='Creazione di API con Django REST Framework.',
        price=44.99,
        stock=20,
        category=books
    )

    print("Creazione carrello per customer_demo...")
    cart = Cart.objects.create(user=customer1)
    CartItem.objects.create(cart=cart, product=laptop, quantity=1)
    CartItem.objects.create(cart=cart, product=python_book, quantity=2)

    print("Creazione ordini...")
    order1 = Order.objects.create(user=customer1, status='DELIVERED')
    OrderItem.objects.create(order=order1, product=smartphone, quantity=1, price_at_purchase=799.99)
    OrderItem.objects.create(order=order1, product=tshirt, quantity=2, price_at_purchase=19.99)

    order2 = Order.objects.create(user=customer2, status='SHIPPED')
    OrderItem.objects.create(order=order2, product=headphones, quantity=1, price_at_purchase=199.99)

    order3 = Order.objects.create(user=customer1, status='PENDING')
    OrderItem.objects.create(order=order3, product=django_book, quantity=1, price_at_purchase=44.99)
    OrderItem.objects.create(order=order3, product=jacket, quantity=1, price_at_purchase=89.99)

    print("Database popolato con successo!")
    print("\nAccount demo:")
    print("  admin_demo / admin12345 - ADMIN")
    print("  manager_demo / manager12345 - MANAGER")
    print("  customer_demo / customer12345 - CUSTOMER")
    print("  mario_rossi / mario12345 - CUSTOMER")


if __name__ == '__main__':
    run()
