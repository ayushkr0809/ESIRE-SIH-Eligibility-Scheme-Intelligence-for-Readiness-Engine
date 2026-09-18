# SIH-ESIRE

## Entrepreneur Scheme Intelligence & Readiness Engine

SIH-ESIRE is an AI-driven platform designed to help entrepreneurs and marginalized communities discover relevant government schemes, understand eligibility requirements, and identify schemes that best match their individual profiles.

The proposed system combines **Large Language Models (LLMs)**, **knowledge graphs**, **dual-score relevance matching**, and a **symbolic rule engine** to provide recommendations that are intelligent, relevant, verifiable, and explainable.

> 🚧 **Project Status:** Under Active Development — Smart India Hackathon (SIH)

---

## 🎯 Problem

Entrepreneurs often face difficulties when trying to find and apply for government schemes because:

* There are a large number of schemes available.
* Eligibility criteria can be complex and difficult to interpret.
* Different schemes have different requirements.
* Users may struggle to identify which schemes are actually relevant to them.
* Government scheme information can be difficult to understand.
* Language barriers can make scheme information less accessible.

SIH-ESIRE aims to simplify this process by analyzing an entrepreneur's profile and intelligently matching it with suitable government schemes.

---

## 💡 Proposed Solution

SIH-ESIRE uses a **Neuro-Symbolic AI architecture** that combines the flexibility of neural models with the reliability of deterministic rule-based reasoning.

The system is designed around the following pipeline:

```text
User Profile
     │
     ▼
┌──────────────────────┐
│   Profile Analysis   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    LLM Intelligence  │
│  Scheme Understanding│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Dual-Score        │
│  Relevance Filtering │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Symbolic Rule       │
│      Engine          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Verified & Relevant  │
│ Scheme Recommendations│
└──────────────────────┘
```

---

## 🧠 Neuro-Symbolic Architecture

### 1. LLM-Based Intelligence

The neural layer uses Large Language Models to understand unstructured and natural-language information.

It is intended to handle:

* Scheme descriptions
* Eligibility requirements
* User profiles
* Natural-language queries
* Scheme benefits
* Required documents
* Multilingual text

The LLM layer helps identify potentially relevant schemes based on semantic understanding rather than relying only on keyword matching.

---

### 2. Dual-Score Recommendation

Potentially relevant schemes are evaluated using a dual-score mechanism.

The scoring layer is intended to consider factors such as:

* Semantic relevance
* User-profile suitability
* Scheme requirements
* Other relevant matching signals

This helps reduce irrelevant recommendations before they reach the final verification stage.

---

### 3. Symbolic Rule Engine

The shortlisted schemes are passed through a deterministic rule-based verification layer.

The rule engine checks explicit eligibility conditions such as:

* Age
* Income
* Location
* Business type
* Entrepreneur category
* Other scheme-specific requirements

Unlike an LLM, the symbolic layer follows predefined rules and conditions, providing a more deterministic eligibility verification mechanism.

---

## 🔗 Knowledge Graph

**Neo4j** is planned as the knowledge graph layer of SIH-ESIRE.

Government schemes contain many relationships between different entities. Neo4j can represent these relationships in a graph structure instead of treating each scheme as an isolated record.

Example:

```text
Entrepreneur
     │
     ├──── belongs_to ────► Entrepreneur Category
     │
     ├──── located_in ─────► State
     │
     └──── operates ───────► Business Type
                                  │
                                  ▼
                               Scheme
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                 provides      requires     available_in
                  Benefit      Document         State
```

This knowledge graph is intended to help the system understand relationships between:

* Entrepreneurs
* Government schemes
* Eligibility criteria
* Business types
* Locations
* Benefits
* Required documents
* Entrepreneur categories

---

## 🗄️ Data Architecture

SIH-ESIRE is planned to use **PostgreSQL and Neo4j for different purposes**.

### PostgreSQL

PostgreSQL will primarily handle structured and transactional application data such as:

* User accounts
* User profiles
* Authentication information
* Applications
* User interactions
* Other structured application data

### Neo4j

Neo4j will be used for the **scheme knowledge graph**, representing relationships between:

* Schemes
* Eligibility criteria
* Entrepreneur categories
* Business types
* Locations
* Benefits
* Documents
* Other scheme-related entities

This separation allows each database to handle the type of data it is best suited for.

---

# 🏗️ Proposed System Architecture

```text
                         ┌─────────────────┐
                         │      USER       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ React Frontend  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ FastAPI Backend │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
      │ PostgreSQL  │      │    Neo4j    │      │ LLM Layer   │
      │             │      │ Knowledge   │      │             │
      │ User &      │      │   Graph     │      │ Scheme &    │
      │ Application │      │             │      │ Profile     │
      │ Data        │      │             │      │ Intelligence│
      └─────────────┘      └──────┬──────┘      └──────┬──────┘
                                  │                    │
                                  └──────────┬─────────┘
                                             ▼
                                    ┌─────────────────┐
                                    │   Dual-Score    │
                                    │     Layer       │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Symbolic Rule   │
                                    │     Engine      │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │     Final       │
                                    │ Recommendations │
                                    └─────────────────┘
```

---

# 🖥️ Current Development Status

## Frontend

The project is currently focused on frontend development.

### Implemented / In Progress

* Landing page
* Login interface
* Signup interface
* Dashboard
* Scheme listing interface
* Scheme information display
* Scheme requirements presentation
* User-oriented navigation
* React component architecture
* Responsive UI development

## Backend

Backend development is planned and will be added progressively.

Planned technologies:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Neo4j
* JWT Authentication

## AI Layer

Planned AI functionality includes:

* LLM-based scheme understanding
* User-profile understanding
* Semantic scheme matching
* Dual-score recommendation mechanism
* Multilingual support

## Verification Layer

Planned verification functionality includes:

* Symbolic rule engine
* Deterministic eligibility verification
* Explainable eligibility results

---

# 🛠️ Technology Stack

| Layer               | Technologies                  |
| ------------------- | ----------------------------- |
| Frontend            | React, Vite, JavaScript, CSS  |
| Backend             | Python, FastAPI, SQLAlchemy   |
| Relational Database | PostgreSQL                    |
| Knowledge Graph     | Neo4j                         |
| AI / NLP            | LLMs, NLP, Neuro-Symbolic AI  |
| Recommendation      | Dual-Score Relevance Matching |
| Verification        | Symbolic Rule Engine          |
| Authentication      | JWT                           |

---

# 📁 Project Structure

The repository currently contains the frontend. Backend and AI components will be added as development progresses.

```text
SIH-ESIRE/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── ...
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── ...
│
├── README.md
├── .gitignore
└── ...
```

The final project structure is expected to evolve into:

```text
SIH-ESIRE/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── ...
│
├── README.md
├── .gitignore
└── ...
```

---

# ⚙️ Getting Started

## Prerequisites

Make sure the following are installed:

* [Node.js](https://nodejs.org/)
* npm
* Git

---

## 1. Clone the Repository

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd SIH-ESIRE
```

---

## 2. Navigate to the Frontend

```bash
cd frontend
```

---

## 3. Install Dependencies

Install all frontend dependencies listed in `package.json`:

```bash
npm install
```

This automatically installs React, React DOM, React Router, and other project dependencies.

---

## 4. Start the Development Server

```bash
npm run dev
```

Vite will display the local development server URL in the terminal.

Usually:

```text
http://localhost:5173
```

Open the displayed URL in your browser.

---

# 👥 Development Setup for Team Members

If you are contributing to SIH-ESIRE:

### Clone the repository

```bash
git clone <repository-url>
cd SIH-ESIRE
```

### Install frontend dependencies

```bash
cd frontend
npm install
```

### Run the frontend

```bash
npm run dev
```

You do **not** need to manually install individual React packages. The dependencies are defined in `package.json`, and `npm install` installs them automatically.

> **Note:** The backend setup, database configuration, and AI services will be documented here once those components are implemented.

---

# 🔐 Environment Variables

Environment variables will be introduced when backend services and external APIs are integrated.

Sensitive information such as:

* Database credentials
* JWT secrets
* LLM API keys
* Neo4j credentials
* Other private configuration

should **never be committed to the repository**.

A `.env.example` file will be provided when environment variables become part of the project setup.

---

# 🗺️ Roadmap

### Frontend

* [x] Initial React/Vite setup
* [x] Landing page
* [x] Login UI
* [x] Signup UI
* [x] Dashboard UI
* [x] Scheme listing interface
* [ ] Final frontend polish
* [ ] Responsive improvements
* [ ] Frontend-backend integration

### Backend

* [ ] FastAPI project setup
* [ ] API architecture
* [ ] JWT authentication
* [ ] PostgreSQL integration
* [ ] SQLAlchemy models
* [ ] User/profile APIs
* [ ] Scheme APIs

### Knowledge Graph

* [ ] Neo4j setup
* [ ] Scheme knowledge graph
* [ ] Entity modelling
* [ ] Relationship modelling
* [ ] Graph-based scheme queries

### AI / Recommendation Engine

* [ ] LLM integration
* [ ] Scheme information processing
* [ ] User-profile understanding
* [ ] Dual-score relevance mechanism
* [ ] Scheme recommendation pipeline
* [ ] Multilingual support

### Verification Engine

* [ ] Symbolic rule engine
* [ ] Eligibility rule representation
* [ ] Deterministic eligibility verification
* [ ] Explainable eligibility results

### Deployment

* [ ] Production configuration
* [ ] Containerization
* [ ] Cloud deployment
* [ ] Monitoring and logging

---

# 🎯 Project Goal

The goal of SIH-ESIRE is to make government schemes **easier to discover, understand, and access**.

By combining:

**LLM Intelligence + Knowledge Graphs + Dual-Score Matching + Symbolic Reasoning**

the system aims to provide recommendations that are:

* **Relevant**
* **Personalized**
* **Verifiable**
* **Explainable**
* **Accessible**

---

# 📌 Project Status

**SIH-ESIRE is currently under active development as part of the Smart India Hackathon (SIH).**

The frontend is currently being developed, while the backend, databases, AI recommendation pipeline, knowledge graph, and symbolic verification engine are planned for subsequent development.

---

## 👨‍💻 Contributors

SIH-ESIRE is being developed collaboratively as part of the Smart India Hackathon.

Contributors will be added as the project progresses.
