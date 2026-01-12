# backend/src/security_audit.py - Audit ultra-personnalisé et accéléré

import pandas as pd
from dependencies import get_llm
from src.rag_setup import retrieve_context
import time
import json
import asyncio
import os
from fastapi.concurrency import run_in_threadpool

CACHE_FILE = "data/last_audit_cache.json"
DATA_FILES = ["data/users.csv", "data/roles.csv", "data/privs.csv"]

async def audit_security():
    start = time.time()
    
    # 1. Vérification du Cache (Si les fichiers n'ont pas changé)
    try:
        last_mtime = max([os.path.getmtime(f) for f in DATA_FILES if os.path.exists(f)], default=0)
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cached = json.load(f)
            if cached.get("timestamp", 0) >= last_mtime:
                print("⚡ Cache utilisé pour Audit Sécurité (0s)")
                return cached["report"]
    except Exception as e:
        print(f"Cache error: {e}")
    try:
        users_df = pd.read_csv('data/users.csv')
        roles_df = pd.read_csv('data/roles.csv')
        privs_df = pd.read_csv('data/privs.csv')


        # Optimisation : On ne garde que les lignes "intéressantes" (OPEN, DBA, ANY) ou les 50 premières
        users_sample = users_df[users_df['account_status'] == 'OPEN'].head(50)
        if users_sample.empty: users_sample = users_df.head(20)
        
        users_str = users_sample.to_string(index=False)
        roles_str = roles_df.head(50).to_string(index=False) # Max 50 roles
        privs_str = privs_df[privs_df['privilege'].str.contains('ANY|DBA', case=False, na=False)].head(50).to_string(index=False)
        if len(privs_str) < 10: privs_str = privs_df.head(20).to_string(index=False)

        open_users = len(users_df[users_df['account_status'] == 'OPEN'])
        any_privs = len(privs_df[privs_df['privilege'].str.contains('ANY', case=False)])
        dba_users = len(roles_df[roles_df['granted_role'].str.contains('DBA', case=False)])

        # Personnalisation : stats et détection changements
        previous_open = 0  # Charge de previous_security.json si existe
        try:
            with open("data/previous_security.json", "r") as f:
                previous = json.load(f)
                previous_open = previous['open_users']
        except:
            previous_open = open_users

        change_note = f"Changements détectés : {open_users - previous_open} users ouverts ajoutés."

        user_context = f"Base utilisateur avec {open_users} users ouverts, {any_privs} ANY, {dba_users} DBA. {change_note}. Orientation DBA : focus moindre privilège, audit."

        score = 100 - (open_users * 2) - (any_privs * 10) - (dba_users * 15)
        score = max(score, 20)

    except Exception as e:
        return {"error": str(e), "score": 0}

    context = "\n".join(retrieve_context("oracle security risks users roles privileges", top_k=3))

    try:
        # Optimisation Quota : 1 seul appel au lieu de 3 (Réduit la charge API de 66%)
        combined_prompt = (
            f"Analyse la sécurité de cette base Oracle.\n\n"
            f"DONNEES UTILISATEURS :\n{users_str}\n\n"
            f"DONNEES ROLES :\n{roles_str}\n\n"
            f"DONNEES PRIVILEGES :\n{privs_str}\n\n"
            f"Instructions :\n"
            f"1. Analyse les risques liés aux utilisateurs/rôles.\n"
            f"2. Analyse les privilèges excessifs.\n"
            f"3. Vérifie les profils de mot de passe (FAILED_LOGIN_ATTEMPTS, etc).\n\n"
            f"REPONDS UNIQUEMENT AU FORMAT JSON VALIDE comme suit :\n"
            f"{{\n"
            f'  "users_analysis": "Analyse critique des utilisateurs...",\n'
            f'  "users_recommendation": "Action concrète pour corriger (ex: Verrouiller user X, Révoquer rôle Y)...",\n'
            f'  "privs_analysis": "Analyse des privilèges...",\n'
            f'  "privs_recommendation": "Action concrète pour les privilèges...",\n'
            f'  "profile_analysis": "Analyse des profils...",\n'
            f'  "profile_recommendation": "Action concrète pour les profils..."\n'
            f"}}"
        )

        response_json_str = await run_in_threadpool(
            get_llm().generate,
            combined_prompt,
            context=context,
            user_context=user_context
        )
        
        # Nettoyage pour garantir le JSON
        response_json_str = response_json_str.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(response_json_str)

        risks_users = analysis.get("users_analysis", "Pas d'analyse")
        rec_users = analysis.get("users_recommendation", "Revoir les comptes utilisateurs")
        
        risks_privs = analysis.get("privs_analysis", "Pas d'analyse")
        rec_privs = analysis.get("privs_recommendation", "Appliquer le principe du moindre privilège")
        
        risks_profile = analysis.get("profile_analysis", "Pas d'analyse")
        rec_profile = analysis.get("profile_recommendation", "Durcir les politiques de mot de passe")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback pour ne pas crasher si le JSON est malformé ou erreur quota
        if "429" in str(e):
             return {"error": "Quota Gemini dépassé (429). Attendez 1 minute.", "score": 0}
        return {"error": f"Erreur analyse partielle : {str(e)}", "score": 0}

    report = {
        "score": score,
        "risks": [
            {
                "severity": "critique", 
                "description": risks_users.strip(), 
                "recommendation": rec_users.strip()
            },
            {
                "severity": "haute", 
                "description": risks_privs.strip(), 
                "recommendation": rec_privs.strip()
            },
            {
                "severity": "moyenne", 
                "description": risks_profile.strip(), 
                "recommendation": rec_profile.strip()
            }
        ],
        "recommendations": [
            rec_users.strip(),
            rec_privs.strip(),
            rec_profile.strip()
        ]
    }

    # Sauvegarde pour détection changements
    with open("data/previous_security.json", "w") as f:json.dump({"open_users": open_users}, f)

    print(f"Audit sécurité en {time.time() - start:.2f}s (Parallélisé)")
    
    # Sauvegarde du Cache
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "report": report
            }, f)
    except: pass
    
    return report