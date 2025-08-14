

# Kindergarten Website Management System 🏫

## 🚀 Getting Started

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/AbdullahRFA/Kindergarten-Website-Management-System.git
cd Kindergarten-Website-Management-System
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  
# On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional but Recommended)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser to explore the platform.

---

## 🛠 Tech Stack

- **Backend:** Django
- **Frontend:** Django Templates
- **Database:** SQLite (default, can be configured)
- **Environment:** Python 3.x

## 📁 Project Structure Highlights

- `kindergarten/` – Core Django app
- `templates/` – HTML templates for admin, teacher, and public views
- `static/` – CSS, JS, and image assets
- `requirements.txt` – All dependencies for easy setup

---





