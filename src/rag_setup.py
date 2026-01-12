try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    HAS_RAG = True
except ImportError:
    HAS_RAG = False

model = None
collection = None

if HAS_RAG:
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        client = chromadb.PersistentClient(path='data/chroma_db')
        collection = client.get_or_create_collection(name='oracle_docs')
        
        # Sample 15-20 documents
        documents = [
            "Oracle Tuning Guide: Use indexes to avoid full table scans.",
            "Best practice: Add hints like /*+ INDEX */ for query optimization.",
            "Security: Apply principle of least privilege - avoid GRANT ANY.",
            "Anomalies: Watch for logins outside business hours.",
            "Optimization patterns: Rewrite subqueries to joins for better performance.",
            "Security patterns: Set password expiration to 90 days.",
            "Anomaly patterns: SQL injection looks like ' OR ''=' in queries.",
            "Backup: Use RMAN for incremental backups.",
            "Restore: Use FLASHBACK for point-in-time recovery.",
            "Performance: Monitor V$SQLSTAT for slow queries.",
            "Audit: Enable unified auditing for better logs.",
            "Roles: Avoid default DBA role for users.",
            "Privileges: Revoke unnecessary system privs.",
            "Profiles: Set FAILED_LOGIN_ATTEMPTS to 5.",
            "Events: Monitor wait events in V$SYSTEM_EVENT.",
            "Index: Create B-tree indexes on frequently filtered columns.",
            "Hints: Use /*+ PARALLEL */ for large queries.",
            "Escalation: Detect GRANT statements on critical roles.",
            "Injection: Look for -- or ; in audit actions.",
            "RTO/RPO: For critical DB, aim RPO <1h.",
            "Security risk: Public role has EXECUTE on dangerous packages like UTL_FILE, UTL_HTTP.",
            "Never grant CREATE ANY PROCEDURE to application users.",
            "Use Oracle Vault or TDE for sensitive data encryption.",
            "Monitor failed logins for brute force attacks.",
            "Use Database Vault to separate duties.",
            "Flashback table requires undo retention and row movement.",
            "PITR requires archive log mode.",
            "Use incremental level 0 + level 1 for efficient backups.",
            "Validate RMAN backups with RESTORE VALIDATE.",
            "Use BLOCK CHANGE TRACKING for faster incremental backups.",
            "Performance: Avoid functions on indexed columns in WHERE.",
            "Use bind variables to avoid hard parsing.",
            "Gather stats regularly with DBMS_STATS.",
            "Use result_cache for repetitive queries.",
            "Partition large tables for better performance and maintenance.",
            "DBA 2026 best practice: Use clear annotations for schema personalization in LLM tools.",
            "For local LLMs with Oracle, assign specific LLM for DBA use cases.",
            "Oracle 26ai: Built-in AI with LLM choice for personalization.",
            "Operationalize AI in 2026: Use guardrails for sensitive info in LLM."
        ]

        # Only add if empty to save time, or just overwrite for demo simplicity
        if collection.count() == 0:
            embeddings = model.encode(documents)
            for i, doc in enumerate(documents):
                collection.add(ids=[str(i)], embeddings=[embeddings[i].tolist()], metadatas=[{"text": doc}])
    except Exception as e:
        print(f"⚠️ RAG Init Error: {e}")
        HAS_RAG = False

def retrieve_context(query, top_k=3):
    if not HAS_RAG or not collection:
        return ["(RAG indisponible - Contexte générique utilisé)"]
    
    try:
        query_emb = model.encode(query).tolist()
        results = collection.query(query_embeddings=[query_emb], n_results=top_k)
        return [meta['text'] for meta in results['metadatas'][0]]
    except Exception:
        return []

if __name__ == "__main__":
    print(retrieve_context("index lent"))