# ESIRE — Eligibility & Scheme Intelligence for Readiness Engine

**ESIRE** is an AI-powered platform designed to help users discover relevant government schemes, understand eligibility requirements, and determine their readiness to apply.

The platform combines **LLM-based intelligence, personalized scheme matching, document readiness, and rule-based eligibility verification** to simplify access to government schemes.

> 🚧 **Project Status:** Under Active Development — Smart India Hackathon (SIH)

---

## 🎯 Problem

Finding and applying for government schemes can be difficult because:

* There are many schemes with different eligibility criteria.
* Requirements can be complex and difficult to understand.
* Users may not know which schemes are relevant to their situation.
* Required documents vary between schemes.
* Language barriers can make information less accessible.
* Users often have to search through multiple sources to find suitable schemes.

ESIRE aims to bring this process into a single, easy-to-use platform.

---

## 💡 Solution

ESIRE takes information about a user and analyzes it against available government schemes.

### Core workflow

```text
              User
                │
                ▼
       ┌─────────────────┐
       │  User Profile   │
       │ & Requirements  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  AI / LLM Layer │
       │ Profile Analysis│
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Scheme Matching │
       │ & Scoring       │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Eligibility &   │
       │ Document Check  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Personalized    │
       │ Recommendations │
       └─────────────────┘
```

---

# 🧠 AI & Recommendation System

ESIRE is designed around a **neuro-symbolic approach**, combining AI-based understanding with deterministic verification.

### LLM Intelligence

The LLM layer can be used to understand:

* User-provided information
* Scheme descriptions
* Eligibility requirements
* Benefits
* Required documents
* Natural-language queries
* Multilingual input

For the prototype, **Ollama** can be used to run local language models.

### Scheme Matching

Candidate schemes can be evaluated using multiple matching signals, including:

* User profile compatibility
* Scheme eligibility requirements
* Semantic relevance
* Location
* Business or applicant category
* Required documents

The resulting scores help identify schemes that are potentially relevant to the user.

### Rule-Based Verification

After scheme matching, explicit eligibility conditions can be checked using deterministic rules.

Examples include:

* Age
* Income
* Location
* Applicant category
* Business type
* Other scheme-specific conditions

This helps separate **AI-based recommendation** from **rule-based eligibility verification**.

---

# 📄 Document Readiness

ESIRE also considers the documents required by schemes.

The system can identify:

* Required documents
* Documents already provided
* Missing documents
* Application readiness

A user can therefore understand not only **which schemes may be suitable**, but also **what is still required to apply**.

---

# 🌐 Multilingual Support

ESIRE is designed with accessibility in mind.

The prototype supports a multilingual interface, with **English, Hindi, and Manipuri** planned/supported across relevant user-facing components.

Users can interact with the platform through a language selected manually or based on available browser language information.

---

# 🗄️ Data Architecture

ESIRE uses different data technologies for different purposes.

### PostgreSQL

Used for structured application data such as:

* Users
* Profiles
* Authentication
* Applications
* Other transactional data

### MongoDB

Can be used for flexible or document-oriented data where appropriate.

### Neo4j

Planned for the scheme knowledge graph.

The graph can represent relationships between:

```text
User
 │
 ├── belongs to ──► Category
 │
 ├── located in ──► State
 │
 └── operates ────► Business Type
                         │
                         ▼
                       Scheme
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Benefit    Document   Eligibility
```

This allows schemes and their relationships to be represented as connected entities rather than isolated records.

---

# 🏗️ System Architecture

```text
                    ┌───────────────┐
                    │     User      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ React + Vite  │
                    │   Frontend    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    │    Backend    │
                    └───────┬───────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   ┌────────────┐    ┌────────────┐    ┌────────────┐
   │ PostgreSQL │    │  MongoDB   │    │   Neo4j    │
   │ Structured │    │ Flexible   │    │ Knowledge  │
   │    Data    │    │    Data    │    │   Graph    │
   └────────────┘    └────────────┘    └─────┬──────┘
                                             │
                                             ▼
                                    ┌────────────────┐
                                    │  AI / Ollama   │
                                    │ Intelligence   │
                                    └───────┬────────┘
                                            │
                                            ▼
                                    ┌────────────────┐
                                    │ Matching &     │
                                    │ Scoring Engine │
                                    └───────┬────────┘
                                            │
                                            ▼
                                    ┌────────────────┐
                                    │ Rule / Z3      │
                                    │ Verification   │
                                    └───────┬────────┘
                                            │
                                            ▼
                                    ┌────────────────┐
                                    │ Recommendations│
                                    └────────────────┘
```

---

# 🖥️ Current Development Status

## Frontend

### Implemented

* Landing page
* Login interface
* Signup interface
* Dashboard
* Profile interface
* Scheme listing
* Scheme details
* Documents interface
* My Schemes interface
* Settings
* Help section
* Protected routes
* Authentication context
* Multilingual UI structure
* React component architecture
* Responsive UI work

### Technology

* React
* Vite
* JavaScript
* CSS
* React Router

---

## Backend

The FastAPI backend is currently being developed.

Current backend structure includes:

* Authentication
* User management
* Scheme APIs
* Document APIs
* System APIs
* Database modules
* Matching services
* Scoring services
* Ollama integration
* OTP service
* Z3 rule engine
* Scheme catalog
* Document extraction

### Technology

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* MongoDB
* Neo4j
* JWT
* Ollama
* Z3

---

# 📁 Project Structure

```text
ESIRE/
│
├── Backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── seed_schemes.json
│   │   │
│   │   ├── db/
│   │   │   ├── mongo.py
│   │   │   ├── neo4j_db.py
│   │   │   └── postgres.py
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── schemes.py
│   │   │   ├── system.py
│   │   │   └── users.py
│   │   │
│   │   ├── services/
│   │   │   ├── catalog.py
│   │   │   ├── extractor.py
│   │   │   ├── matching.py
│   │   │   ├── ollama.py
│   │   │   ├── otp.py
│   │   │   ├── scoring.py
│   │   │   └── z3_engine.py
│   │   │
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── security.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── Frontend/
│   ├── public/
│   ├── src/
│   │   ├── Components/
│   │   ├── Pages/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── i18n/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

# 🛠️ Technology Stack

| Layer            | Technologies                 |
| ---------------- | ---------------------------- |
| Frontend         | React, Vite, JavaScript, CSS |
| Backend          | Python, FastAPI, SQLAlchemy  |
| Database         | PostgreSQL, MongoDB          |
| Knowledge Graph  | Neo4j                        |
| AI               | Ollama, LLMs                 |
| Recommendation   | Profile Matching & Scoring   |
| Verification     | Rule Engine, Z3              |
| Authentication   | JWT                          |
| Containerization | Docker                       |

---

# ⚙️ Getting Started

## Prerequisites

Install:

* Node.js
* npm
* Python
* Git
* PostgreSQL
* Docker *(optional)*
* Ollama *(required for local LLM functionality)*

---

## Clone the Repository

```bash
git clone https://github.com/ayushkr0809/ESIRE-SIH-Eligibility-Scheme-Intelligence-for-Readiness-Engine.git

cd ESIRE-SIH-Eligibility-Scheme-Intelligence-for-Readiness-Engine
```

---

## Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

The Vite development server will provide a local URL, usually:

```text
http://localhost:5173
```

---

## Backend Setup

From the project root:

```bash
cd Backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🔐 Environment Variables

Sensitive configuration should **never be committed** to the repository.

Examples include:

* Database credentials
* JWT secrets
* Neo4j credentials
* MongoDB credentials
* API keys
* Other private configuration

Use the provided `.env.example` files as templates for local configuration.

---

# 🗺️ Roadmap

### Frontend

* [x] Landing page
* [x] Authentication UI
* [x] Dashboard
* [x] Scheme interface
* [x] Profile interface
* [x] Documents interface
* [x] Settings
* [x] Multilingual UI structure
* [ ] Complete backend integration
* [ ] Final UI polish

### Backend

* [x] FastAPI structure
* [x] Authentication structure
* [x] Scheme APIs
* [x] User APIs
* [x] Document APIs
* [x] Matching services
* [x] Scoring services
* [x] Ollama service
* [x] Z3 engine structure
* [ ] Complete production database integration
* [ ] Full frontend-backend integration

### AI & Recommendation

* [x] Ollama integration structure
* [x] Matching service structure
* [x] Scoring service structure
* [ ] Complete LLM recommendation pipeline
* [ ] Improved semantic matching
* [ ] Multilingual AI processing

### Knowledge Graph

* [x] Neo4j integration structure
* [ ] Scheme graph construction
* [ ] Entity modelling
* [ ] Relationship modelling
* [ ] Graph-based recommendation queries

### Verification

* [x] Rule engine structure
* [x] Z3 integration structure
* [ ] Complete eligibility rule modelling
* [ ] Explainable verification results
* [ ] Document-aware eligibility verification

### Deployment

* [x] Docker configuration
* [ ] Production configuration
* [ ] Cloud deployment
* [ ] Monitoring and logging

---

# 🎯 Project Goal

The goal of ESIRE is to make government schemes **easier to discover, understand, and apply for**.

By combining:

```text
AI Intelligence
       +
Scheme Matching
       +
Knowledge Graphs
       +
Document Readiness
       +
Deterministic Verification
```

ESIRE aims to provide users with **relevant, personalized, verifiable, and understandable scheme recommendations**.

---

# 👥 Team

ESIRE is being developed collaboratively as part of the **Smart India Hackathon (SIH)**.

Team members and contributors will be documented as the project progresses.

---

## 📌 Status

**ESIRE is currently under active development for Smart India Hackathon (SIH).**

The project is evolving from a frontend prototype into an integrated platform combining web technologies, backend services, databases, AI-based recommendation, knowledge graphs, and deterministic eligibility verification.
