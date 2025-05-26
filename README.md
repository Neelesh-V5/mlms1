
---

# 🧳 Migrant Labour Management System (MLMS)

A digital platform developed to improve the working conditions of migrant labourers in Tamil Nadu by facilitating direct connections with employers, ensuring fair wages, providing multilingual support, and giving access to relevant government welfare schemes.

---

## 📘 Overview

The MLMS aims to:

* Eliminate exploitation by middlemen
* Enable direct wage negotiation between labourers and employers
* Improve awareness and access to welfare schemes
* Support multiple Indian languages for better communication
* Provide grievance redressal, job search, and application tracking functionalities

---

## 👥 Team Members

| Name        | Register No. |
| ----------- | ------------ |
| Devashish S | 23Z315       |
| Githendra S | 23Z322       |
| Neelesh V   | 23Z350       |

---

## 🧠 Problem Statement

> “How might we develop a versatile and dynamic website with unique ID numbers to efficiently address migrant labour issues in Tamil Nadu, enabling smooth registration, tracking, and timely support while ensuring ease of use and accessibility?”

---

## 🌐 Features

* ✅ Worker & Employer Registration with Unique IDs
* 🔍 Job Search & Matching Engine
* 💬 Wage Negotiation Support
* 🛠️ Grievance Redressal System
* 📚 Welfare Scheme Portal
* 🌏 Multilingual Support
* 🔐 Secure Login & Password Recovery
* 📈 Admin Dashboard & Tracking

---

## 🛠 Tech Stack

| Layer      | Technology            |
| ---------- | --------------------- |
| Frontend   | HTML, CSS, JavaScript |
| Backend    | Python (Flask)        |
| Database   | SQLite3               |
| Hosting    | PythonAnywhere        |
| Versioning | Git + GitHub          |

---

## 📂 Project Structure

```
mlms1/
├── static/
├── templates/
├── uploads/
├── app.py
├── database.db
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Neelesh-V5/mlms1.git
cd mlms1
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask server

```bash
python app.py
```

### 5. Visit the app

Open `http://localhost:5000` in your browser.

---

## 🧪 Testing

The system has been tested with detailed test cases across multiple use cases:

* ✔ Worker Registration
* ✔ Employer Registration
* ✔ Job Application Process
* ✔ Grievance Handling
* ✔ Login/Authentication
* ✔ Government Scheme Access


---

## 🧩 Architecture

* **Backend**: Flask handles routes, sessions, and API calls.
* **Database**: SQLite3 stores user, job, grievance, and scheme data.
* **Frontend**: Jinja2 templates render dynamic UI with multilingual text support.
* **Security**: Passwords hashed via Werkzeug; Role-based access control (RBAC).

---

## 🌐 Live Links

| Platform           | URL                                                        |
| ------------------ | ---------------------------------------------------------- |
| GitHub Repo        | [View Repo](https://github.com/Neelesh-V5/mlms1)           |
| GitHub Pages       | [View Pages](https://neelesh-v5.github.io/mlms1/)          |
| Live Demo (Hosted) | [PythonAnywhere](https://neilthedev05.pythonanywhere.com/) |

---

## 🛡 License

MIT License. See [`LICENSE`](LICENSE) file.

---

