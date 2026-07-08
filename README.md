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