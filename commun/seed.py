import random
from datetime import datetime, timedelta
from commun.database import Database


def initialiser_donnees():
    """Pré-remplit la base de données si elle est vide. Exécuté silencieusement."""
    db = Database()

    # Si la table missions n'est pas vide, on ne fait rien
    if db.lire("SELECT COUNT(*) as c FROM missions")[0]["c"] > 0:
        db.conn.close()
        return

    # --- 1. MISSIONS ---
    missions = [
        ("Sentinel", "ESA", "2014-04-03", "actif", "Observation terrestre"),
        ("Starlink", "SpaceX", "2019-05-23", "actif", "Internet global"),
        ("Tianwen", "CNSA", "2020-07-23", "actif", "Exploration martienne"),
    ]
    for m in missions:
        db.ecrire(
            "INSERT INTO missions (nom, agence, date_lancement, statut, objectif) VALUES (?, ?, ?, ?, ?)",
            m
        )

    # --- 2. SATELLITES ---
    satellites = [
        (1, "Sentinel-2A", 786000, 7.45, 98.5, "actif"),
        (1, "Sentinel-2B", 786000, 7.45, 98.5, "actif"),
        (2, "Starlink-1001", 550000, 7.6, 53.0, "actif"),
        (2, "Starlink-1002", 550000, 7.6, 53.0, "actif"),
        (3, "Tianwen-Orbiter", 400000, 4.8, 87.0, "actif"),
    ]
    for s in satellites:
        db.ecrire(
            "INSERT INTO satellites (id_mission, nom, altitude, vitesse, inclinaison, statut) VALUES (?, ?, ?, ?, ?, ?)",
            s
        )

    # --- 3. EVENEMENTS (20 historiques) ---
    types = ["Telemetrie", "Alerte", "Commande"]
    messages = {
        "Telemetrie": ["Données télémétriques normales", "Capteurs opérationnels", "Altitude stable"],
        "Alerte": ["Batterie faible", "Anomalie thermique détectée", "Perte de signal temporaire"],
        "Commande": ["Ajustement orbital effectué", "Calibration terminée", "Mise à jour firmware"],
    }
    
    for _ in range(20):
        sat = random.choice(satellites)
        t = datetime.now() - timedelta(hours=random.randint(0, 48))
        typ = random.choice(types)
        
        db.ecrire(
            """INSERT INTO evenements 
               (id_satellite, horodatage, type_evenement, message, batterie, temperature)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                sat[0], 
                t.strftime("%Y-%m-%d %H:%M:%S"), 
                typ,
                random.choice(messages[typ]),
                round(random.uniform(15, 100), 1),  # Batterie (inclut des valeurs < 30% pour tester les couleurs)
                round(random.uniform(-20, 60), 1)   # Température
            )
        )

    db.conn.close()


if __name__ == "__main__":
    initialiser_donnees()