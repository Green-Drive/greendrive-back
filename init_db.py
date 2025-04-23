import os
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

def wait_for_postgres():
    """Attend que PostgreSQL soit prêt"""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Vérifier si le conteneur est en cours d'exécution
            subprocess.run(
                "docker ps | grep telemetry_db",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Vérifier si la base de données est accessible
            subprocess.run(
                "pg_isready -h localhost -p 5432",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except subprocess.CalledProcessError:
            retry_count += 1
            time.sleep(2)
            print(f"Attente de PostgreSQL... Tentative {retry_count}/{max_retries}")
    
    return False

def init_database():
    if not wait_for_postgres():
        print("Impossible de se connecter à PostgreSQL. Vérifiez que le conteneur est en cours d'exécution.")
        return

    # Récupérer les variables d'environnement
    db_name = os.getenv("POSTGRES_DB", "telemetry_db")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")

    # Commande pour activer l'extension TimescaleDB
    enable_timescaledb_cmd = f"docker exec telemetry_db psql -U {db_user} -d {db_name} -c 'CREATE EXTENSION IF NOT EXISTS timescaledb'"

    try:
        subprocess.run(enable_timescaledb_cmd, shell=True, check=True)
        print("Extension TimescaleDB activée avec succès")
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

if __name__ == "__main__":
    init_database() 