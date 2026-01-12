import oracledb
import pandas as pd
from sqlalchemy import create_engine
import os

# Création du dossier data si nécessaire (au démarrage du backend)
os.makedirs('data', exist_ok=True)

def extract_data(config: dict) -> str:
    """
    Extrait les données Oracle en utilisant la configuration fournie par l'utilisateur.
    
    config = {
        "host": "localhost",
        "port": 1521,
        "service": "freepdb1",
        "user": "imane",
        "password": "MyPassword123"
    }
    
    Retourne un message de succès ou d'erreur.
    """
    try:
        host = config["host"]
        port = int(config["port"])
        service = config["service"]
        user = config["user"]
        password = config["password"]

        # Construction du DSN
        dsn = oracledb.makedsn(host=host, port=port, service_name=service)

        # Chaîne de connexion SQLAlchemy
        connection_string = f"oracle+oracledb://{user}:{password}@{dsn}"

        # Création de l'engine
        engine = create_engine(
            connection_string,
            thick_mode=False,  # Mode thin
            pool_size=5,
            max_overflow=10,
            echo=False
        )

        print(f"Connexion réussie à {user}@{host}:{port}/{service} via SQLAlchemy !")

        # 1. Utilisateurs
        users_df = pd.read_sql("""
            SELECT username, account_status, profile, created
            FROM dba_users
            WHERE account_status IN ('OPEN', 'LOCKED', 'EXPIRED')
        """, engine)
        users_df.to_csv('data/users.csv', index=False)

        # 2. Rôles accordés
        roles_df = pd.read_sql("""
            SELECT grantee, granted_role
            FROM dba_role_privs
            WHERE grantee IN (SELECT username FROM dba_users)
        """, engine)
        roles_df.to_csv('data/roles.csv', index=False)

        # 3. Privilèges système
        privs_df = pd.read_sql("""
            SELECT grantee, privilege
            FROM dba_sys_privs
        """, engine)
        privs_df.to_csv('data/privs.csv', index=False)

        # 4. Logs d'audit unifiés
        try:
            audit_df = pd.read_sql("""
                SELECT event_timestamp, dbusername, action_name, object_schema, object_name, sql_text
                FROM unified_audit_trail
                WHERE event_timestamp > SYSDATE - 7
                ORDER BY event_timestamp DESC
                FETCH FIRST 200 ROWS ONLY
            """, engine)
            audit_df.to_json('data/synthetic_logs.json', orient='records', date_format='iso')
            print(f"{len(audit_df)} logs d'audit extraits")
        except Exception as e:
            print("Unified audit non activé ou vide :", e)
            pd.DataFrame().to_json('data/synthetic_logs.json', orient='records')

        # 5. Requêtes lentes
        slow_queries = pd.read_sql("""
            SELECT sql_id, sql_text, executions, elapsed_time/1000000 AS elapsed_sec,
                   disk_reads, buffer_gets
            FROM v$sql
            WHERE parsing_schema_name NOT IN ('SYS', 'SYSTEM')
              AND executions > 0
            ORDER BY elapsed_time DESC
            FETCH FIRST 20 ROWS ONLY
        """, engine)
        slow_queries.to_csv('data/slow_queries.csv', index=False)
        print(f"{len(slow_queries)} requêtes lentes extraites")

        print("Extraction terminée ! Données sauvegardées dans data/")
        return f"Succès : données extraites de {user}@{host}/{service}"

    except Exception as e:
        error_msg = f"Erreur lors de l'extraction : {str(e)}"
        print(error_msg)
        return error_msg


# Pour test local (si tu lances le fichier directement)
if __name__ == "__main__":
    test_config = {
        "host": "localhost",
        "port": 1521,
        "service": "freepdb1",
        "user": "system",
        "password": "MyPassword123"
    }
    print(extract_data(test_config))