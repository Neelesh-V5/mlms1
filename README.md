# 🧳 Migrant Labour Management System (MLMS)

A digital platform developed to improve the working conditions of migrant labourers in Tamil Nadu by facilitating direct connections with employers, ensuring fair wages, providing multilingual support, and giving access to relevant government welfare schemes.

---


## 📘 Overview

The **Migrant Labour Management System (MLMS)** is a comprehensive web application developed to streamline and safeguard the employment journey of migrant workers in Tamil Nadu. As a state with a growing influx of migrant labourers, Tamil Nadu faces challenges in managing worker identity, job access, fair compensation, and welfare benefits. The MLMS project addresses these gaps by:

* Enabling **centralized digital registration** for labourers and employers
* Generating **unique digital IDs** to authenticate worker identities
* Allowing **migrant workers to browse and apply** for jobs without third-party interference
* Empowering employers to **post verified job offers** directly
* Providing **transparent wage information** and enabling **direct negotiation**
* Offering **multilingual support** to break language barriers
* Supporting access to **government welfare schemes** with eligibility information
* Facilitating **grievance redressal mechanisms** and **admin-level resolution**

Designed with inclusivity and usability in mind, MLMS aims to bridge the gap between migrant workers, employers, and government services—ensuring dignity, fairness, and opportunity for one of the most vulnerable sections of the workforce.

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

