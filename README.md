# 🗄️ Oracle IA Platform - Administration Intelligente

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B.svg)](https://streamlit.io/)

> **Plateforme d'administration Oracle propulsée par Intelligence Artificielle générative**  
> Automatisation complète : Audit de sécurité, Optimisation SQL, Détection d'anomalies, Backup intelligent & Chatbot conversationnel

---

## 📋 Table des matières

- [🎯 Aperçu rapide](#-aperçu-rapide)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🚀 Installation rapide (5 min)](#-installation-rapide-5-min)
- [💻 Utilisation](#-utilisation)

---

## 🎯 Aperçu rapide

**Oracle IA Platform** transforme l'administration Oracle traditionnelle en expérience intelligente et conversationnelle. Posez vos questions en français, obtenez des analyses expertes et des recommandations actionnables en temps réel.

### Pourquoi ce projet ?

- ❌ **Avant** : Heures passées à analyser les vues système, chercher dans la documentation, déboguer les requêtes lentes
- ✅ **Après** : Chatbot IA répond instantanément, détecte les anomalies, optimise automatiquement les requêtes

### Technologies de pointe

```
🐍 Python 3.11       │ 🚀 FastAPI 0.115      │ 🎨 Streamlit 1.38
🤖 Groq (Llama 3)    │ 📚 ChromaDB (RAG)     │ 🗄️ Oracle 19c+
```

---

## ✨ Fonctionnalités

### 🔒 1. Audit de Sécurité Intelligent
- **Score de sécurité** (0-100) calculé automatiquement
- Détection des risques : comptes privilégiés, mots de passe faibles, privilèges excessifs
- Recommandations IA personnalisées selon les best practices Oracle

### ⚡ 2. Optimisation de Requêtes SQL
- Identification automatique des requêtes lentes (> 1s)
- Analyse du plan d'exécution par l'IA
- Suggestions d'index, hints SQL, réécriture de requêtes

### 🔍 3. Détection d'Anomalies
- Classification en temps réel : NORMAL / SUSPECT / CRITIQUE
- Analyse contextuelle (heure, utilisateur, action, privilèges)
- Alerting immédiat sur comportements inhabituels

### 💾 4. Backup Intelligent
- Génération de stratégies personnalisées (RPO/RTO/Budget)
- Scripts RMAN automatiques et optimisés
- Planification cron intégrée

### 🔄 5. Restauration Guidée
- Scénarios : Point-in-Time Recovery, Table Recovery, Tablespace
- Commandes RMAN générées automatiquement
- Estimation du temps de restauration

### 💬 6. Chatbot Conversationnel
- Questions en langage naturel
- RAG sur documents Oracle officiels

---

### Flux de données

1. **Extraction** : `V$SQL` → CSV toutes les 5 min
2. **Vectorisation** : Documents Oracle → ChromaDB (embeddings)
3. **Question utilisateur** → Recherche RAG → Contexte enrichi
4. **Génération IA** : LLM → Réponse personnalisée
5. **Affichage** : Streamlit

---

## 🚀 Installation rapide (5 min)

### Prérequis

```bash
✅ Python 3.11+
✅ Oracle Database 19c/21c (ou Oracle XE)
✅ Clé API Groq (ou Gemini)
✅ 8 GB RAM minimum
```

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone https://github.com/imanelujen/DbaAI.git
cd DbaAI

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer dépendances
pip install fastapi uvicorn streamlit oracledb pandas sqlalchemy requests python-dotenv chromadb sentence-transformers

# 4. Configuration Oracle & LLM
cp .env.example .env
nano .env  # Éditer avec vos credentials
```

**Fichier `.env` :**
```env
# Oracle Database
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=freepdb1
ORACLE_USER=system
ORACLE_PASSWORD=votre_mot_de_passe

# LLM Keys
GROK_API_KEY=votre_cle_groq
GOOGLE_API_KEY=votre_cle_gemini
```

```bash
# 5. Initialiser la base vectorielle (RAG)
python src/rag_setup.py
# ✅ documents vectorisés dans ChromaDB

# 6. Lancer le BACKEND (terminal 1)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 🚀 Backend disponible : http://localhost:8000

# 7. Lancer le FRONTEND (terminal 2)
streamlit run src/dashboard.py --server.port 8501

# Accès :
# - Frontend : http://localhost:8501
# - Backend : http://localhost:8000
```

---

## 💻 Utilisation

### 1️⃣ Connexion à Oracle

```
1. Ouvrez http://localhost:8501
2. Remplissez le formulaire :
   - Host : localhost
   - Port : 1521
   - Service : freepdb1
   - User : system
   - Password : ****

3. Cliquez " Connexion"
4. ✅ Données extraites et analysées
```

### 2️⃣ Navigation dans les modules

**🏠 Accueil** : Vue d'ensemble de la plateforme  
**🔒 Sécurité** : Audit complet + score + recommandations  
**⚡ Performance** : Liste des requêtes lentes + optimisations  
**🔍 Anomalies** : Détection en temps réel des comportements suspects  
**💾 Sauvegardes** : Génération de stratégies personnalisées  
**💬 Chatbot** : Posez vos questions  

### 3️⃣ Exemples de questions au Chatbot

```
💬 "Pourquoi ma requête SELECT * FROM orders WHERE customer_id=123 est lente ?"

🤖 Réponse :
Votre requête effectue un FULL TABLE SCAN car il n'y a pas d'index sur CUSTOMER_ID.

📋 Recommandations :
1. Créer un index : CREATE INDEX idx_orders_cust ON orders(customer_id);
2. Ajouter un hint : /*+ INDEX(orders idx_orders_cust) */
3. Temps estimé après optimisation : 50ms au lieu de 2.3s

📚 Source : Oracle Performance Tuning Guide, Section 8.2
```

```
💬 "Mon utilisateur HR a-t-il trop de privilèges ?"

🤖 Réponse :
⚠️ RISQUE ÉLEVÉ détecté :

L'utilisateur HR possède :
- SYSDBA (privilège système critique)
- DELETE ANY TABLE
- DROP ANY TABLE

🔴 Violation du principe du moindre privilège.

💡 Recommandations :
1. REVOKE sysdba FROM hr;
2. Créer un rôle métier : CREATE ROLE hr_manager;
3. GRANT SELECT, INSERT, UPDATE ON hr.employees TO hr_manager;

📚 Source : Oracle Security Best Practices
```

## 🏆 Auteurs

**CHIKH Imane** - [GitHub](https://github.com/imanelujen) 
**BAHADOU Douaa** - [GitHub](https://github.com/DOUAA575) 

<div align="center">

**⭐ Si ce projet vous a aidé, n'oubliez pas de lui donner une étoile sur GitHub ! ⭐**

</div>
