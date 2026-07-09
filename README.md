# E-Commerce REST API

**Studente:** Lorenzo Malavolti

**Tipo di progetto:** REST API

**Framework:** Django REST Framework

---

## Descrizione

API REST per una piattaforma e-commerce che consente la
gestione di prodotti, categorie, carrelli e ordini.
Il sistema implementa autenticazione JWT e permessi
basati su ruoli (Admin, Manager, Customer).

---

## Funzionalità per ruolo

### Customer

- Registrazione e login
- Visualizzazione dei prodotti e delle categorie
- Gestione del proprio carrello (aggiunta, rimozione, svuotamento)
- Checkout e creazione di ordini
- Visualizzazione dei propri ordini

### Manager

- Tutte le funzionalità del Customer
- Creazione, aggiornamento e cancellazione di prodotti e categorie
- Visualizzazione di tutti gli ordini
- Aggiornamento dello stato degli ordini (es. da "in lavorazione" a "spedito")

### Admin

- Tutte le funzionalità del Manager
- Gestione degli utenti (lista, eliminazione)

___

## Installazione locale

```bash
#1. Clona il repository
git clone https://github.com/mala25ctrl/ppm-ecommerce-rest-api.git
cd ppm-ecommerce-rest-api

#2. Crea e attiva il virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

#3. Installa le dipendenze
pip install -r requirements.txt

#4. Applica le migrazioni
python manage.py migrate

#5. Carica i dati demo
python manage.py loaddata fixtures/initial_data.json

#6. Avvia il server
python manage.py runserver

```

---

## Database

il file `db.sqlite3` è incluso nel repository e contiene dati demo precaricati.
In alternativa, è possibile ricaricare i dati con:

```bash
python manage.py loaddata fixtures/initial_data.json
```

---

## Account demo

| Username      | Password      | Ruolo    |
|---------------|---------------|----------|
| admin_demo    | admin12345    | ADMIN    |
| manager_demo  | manager12345  | MANAGER  |
| customer_demo | customer12345 | CUSTOMER |
| mario_rossi   | mario12345    | CUSTOMER |

---

## Documentazione API

### Swagger UI

Disponibile all'indirizzo: `http://127.0.0.1:8000/api/schema/swagger-ui/`

### Endpoint

#### Autenticazione

| Metodo | URL                | Auth | Ruolo | Descrizione                       |
|--------|--------------------|------|-------|-----------------------------------|
| POST   | /api/auth/login/   | No   | Tutti | Login e ottenimento del token JWT |
| POST   | /api/auth/refresh/ | No   | Tutti | Refresh del token JWT             |

#### Utenti

| Metodo    | URL                | Auth | Ruolo               | Descrizione                      |
|-----------|--------------------|------|---------------------|----------------------------------|
| POST      | /api/users/        | No   | Tutti               | Registrazione di un nuovo utente |
| GET       | /api/users/        | JWT  | Admin               | Lista di tutti gli utenti        |
| GET       | `/api/users/{id}/` | JWT  | Proprietario, ADMIN | Dettaglio utente                 |
| PUT/PATCH | `/api/users/{id}/` | JWT  | Proprietario, ADMIN | Modifica utente                  |
| DELETE    | `/api/users/{id}/` | JWT  | ADMIN               | Elimina utente                   |

#### Categorie

| Metodo    | URL                     | Auth | Ruolo          | Descrizione         |
|-----------|-------------------------|------|----------------|---------------------|
| GET       | `/api/categories/`      | No   | Tutti          | Lista categorie     |
| GET       | `/api/categories/{id}/` | No   | Tutti          | Dettaglio categoria |
| POST      | `/api/categories/`      | JWT  | MANAGER, ADMIN | Crea categoria      |
| PUT/PATCH | `/api/categories/{id}/` | JWT  | MANAGER, ADMIN | Modifica categoria  |
| DELETE    | `/api/categories/{id}/` | JWT  | MANAGER, ADMIN | Elimina categoria   |

#### Prodotti

| Metodo    | URL                   | Auth | Ruolo          | Descrizione        |
|-----------|-----------------------|------|----------------|--------------------|
| GET       | `/api/products/`      | No   | Tutti          | Lista prodotti     |
| GET       | `/api/products/{id}/` | No   | Tutti          | Dettaglio prodotto |
| POST      | `/api/products/`      | JWT  | MANAGER, ADMIN | Crea prodotto      |
| PUT/PATCH | `/api/products/{id}/` | JWT  | MANAGER, ADMIN | Modifica prodotto  |
| DELETE    | `/api/products/{id}/` | JWT  | MANAGER, ADMIN | Elimina prodotto   |

#### Carrello

| Metodo | URL                           | Auth | Ruolo    | Descrizione                      |
|--------|-------------------------------|------|----------|----------------------------------|
| GET    | `/api/cart/me/`               | JWT  | CUSTOMER | Visualizza il proprio carrello   |
| POST   | `/api/cart/add_item/`         | JWT  | CUSTOMER | Aggiunge prodotto al carrello    |
| DELETE | `/api/cart/remove_item/{id}/` | JWT  | CUSTOMER | Rimuove un articolo dal carrello |
| DELETE | `/api/cart/clear/`            | JWT  | CUSTOMER | Svuota il carrello               |

#### Ordini

| Metodo | URL                               | Auth | Ruolo          | Descrizione                 |
|--------|-----------------------------------|------|----------------|-----------------------------|
| GET    | `/api/orders/me/`                 | JWT  | CUSTOMER       | Visualizza i propri ordini  |
| GET    | `/api/orders/all/`                | JWT  | MANAGER, ADMIN | Visualizza tutti gli ordini |
| POST   | `/api/orders/checkout/`           | JWT  | CUSTOMER       | Crea ordine dal carrello    |
| PATCH  | `/api/orders/{id}/update_status/` | JWT  | MANAGER, ADMIN | Aggiorna stato ordine       |

---

## Workflow HTTPie

### Installazione HTTPie

```bash
pip install httpie
```

### URL base locale

```
BASE_URL=http://127.0.0.1:8000/api
```

### URL base deployed

```
BASE_URL=
```

### 1. Registrazione utente

```bash
http POST $BASE_URL/api/users/ username=nuovo_utente email=utente@test.com password=password123
```

### 2. Login e ottenimento token

```bash
http POST $BASE_URL/api/auth/login/ username=customer_demo password=customer12345
```

Copia il valore del campo `access` dalla risposta.

### 3. Visualizza prodotti (senza token)

```bash
http GET $BASE_URL/api/products/
```

### 4. Visualizza carrello

```bash
http GET $BASE_URL/api/cart/me/ "Authorization: Bearer "
```

### 5. Aggiungi prodotto al carrello

```bash
http POST $BASE_URL/api/cart/add_item/ "Authorization: Bearer " product_id=1 quantity=2
```

### 6. Checkout

```bash
http POST $BASE_URL/api/orders/checkout/ "Authorization: Bearer "
```

### 7. Visualizza i propri ordini

```bash
http GET $BASE_URL/api/orders/me/ "Authorization: Bearer "
```

### 8. Login come Manager

```bash
http POST $BASE_URL/api/auth/login/ username=manager_demo password=manager12345
```

### 9. Crea una categoria (solo Manager/Admin)

```bash
http POST $BASE_URL/api/categories/ "Authorization: Bearer " name="Nuova Categoria" slug="nuova-categoria"
```

### 10. Visualizza tutti gli ordini (solo Manager/Admin)

```bash
http GET $BASE_URL/api/orders/all/ "Authorization: Bearer "
```

### 11. Aggiorna stato ordine (solo Manager/Admin)

```bash
http PATCH $BASE_URL/api/orders/1/update_status/ "Authorization: Bearer " status=SHIPPED
```

### 12. Testa azione vietata (Customer tenta di vedere tutti gli ordini)

```bash
http GET $BASE_URL/api/orders/all/ "Authorization: Bearer "
# Risposta attesa: 403 Forbidden
```

---

## Deployment

URL:

---

## Testing

Il progetto include 40 test di integrazione eseguibili con:

```bash
python manage.py test
```

Il workflow CI su GitHub Actions esegue automaticamente tutti i test ad ogni push.