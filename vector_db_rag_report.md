# Rapport Technique : Vector Database & Architecture RAG

Ce rapport détaille l'implémentation de la Base de Données Vectorielle et du système RAG (Retrieval-Augmented Generation) au sein de la plateforme "Virtual DBA".

## 1. Vue d'Ensemble de l'Architecture

Le système utilise une architecture **RAG Hybride** pour fournir des réponses précises et contextuelles. Il combine deux sources d'information :
1.  **Connaissance Statique (Vector DB)** : Une base de connaissances experte sur les bonnes pratiques Oracle.
2.  **Contexte Dynamique (Live Data)** : Des données temps réel extraites de votre base de données Oracle (utilisateurs, logs, performances).

### Schéma de Flux de Données

```mermaid
graph TD
    User[Utilisateur] -->|Question| API[API Backend]
    
    subgraph "Système RAG (Connaissance)"
        API -->|1. Encodage Question| EmbedModel[Sentence Transformer<br/>all-MiniLM-L6-v2]
        EmbedModel -->|2. Recherche Sémantique| VectorDB[(ChromaDB)]
        VectorDB -->|3. Documents Pertinents| API
    end
    
    subgraph "Extraction Live"
        OracleDB[(Oracle Database)] -->|SQL| Extractor[Data Extractor]
        Extractor -->|CSV/JSON| LiveContext[Contexte Live]
        LiveContext --> API
    end
    
    API -->|4. Prompt Enrichi (Question + Docs + Live Data)| LLM[LLM Engine<br/>(Groq/Gemini)]
    LLM -->|5. Réponse Expert| User
```

## 2. Composants Techniques

### A. Base de Données Vectorielle (Vector DB)
Nous utilisons **ChromaDB** (`src/rag_setup.py`), une base de données vectorielle open-source embarquée.
*   **Rôle** : Stocker des "chunks" (morceaux) textuels de documentation experte (tuning, sécurité, backup) sous forme de vecteurs mathématiques.
*   **Persistance** : Les données sont sauvegardées localement dans `data/chroma_db`.

### B. Modèle d'Embedding
Pour transformer le texte en vecteurs (nombres), nous utilisons **SentenceTransformers**.
*   **Modèle** : `all-MiniLM-L6-v2`.
*   **Pourquoi ?** C'est un modèle léger, très rapide et optimisé pour la recherche sémantique (Semantic Search). Il permet de comprendre que "requête lente" est sémantiquement proche de "problème de performance SQL", même sans mots-clés exacts.

### C. Le Processus RAG (Retrieval-Augmented Generation)
1.  **Indexation (Au démarrage)** :
    *   Le système charge une liste de ~40 "documents experts" (ex: *"Use incremental level 0 + level 1 for efficient backups"*).
    *   Il calcule les embeddings (vecteurs) de ces documents.
    *   Il les stocke dans ChromaDB.

2.  **Récupération (À la demande)** :
    *   Quand l'utilisateur pose une question (ex: "Comment optimiser mon backup ?").
    *   La question est convertie en vecteur.
    *   ChromaDB trouve les 3 documents les plus proches "cosine similarity".
    *   **Résultat** : Le système récupère les règles spécifiques aux backups RMAN.

3.  **Génération (LLM)** :
    *   Le système construit un prompt final contenant :
        *   L'instruction système ("Tu es un expert Oracle DBA...").
        *   Le **Contexte RAG** (Les documents récupérés).
        *   Le **Contexte Utilisateur** (Métriques réelles de la base, si disponibles).
        *   La question de l'utilisateur.
    *   Le LLM génère alors une réponse qui est à la fois théoriquement juste (grâce au RAG) et adaptée à votre situation (grâce au contexte live).

## 3. Avantages de cette Approche

*   **Précision** : Le LLM n'invente pas (moins d'hallucinations) car il se base sur les documents fournis.
*   **Confidentialité** : Vos données sensibles restent en local (ChromaDB est local). Seul le contexte nécessaire est envoyé au LLM.
*   **Mise à jour facile** : Pour ajouter une nouvelle connaissance (ex: "Nouvelle règle de sécurité 2026"), il suffit d'ajouter une ligne dans la liste `documents` de `rag_setup.py`. Pas besoin de réentraîner le modèle.

## 4. Pistes d'Amélioration (Next Steps)

Actuellement, la base de connaissances RAG est statique (codée en dur). Pour passer à l'échelle "Production", nous pourrions :
*   **PDF Ingestion** : Ajouter un script pour lire vos vrais PDF de documentation interne et les insérer dans ChromaDB.
*   **Feedback Loop** : Permettre aux DBAs de "voter" pour les meilleures réponses et enrichir la base vectorielle automatiquement.
