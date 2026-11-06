import os

# Chemin de la base de données (à la racine du projet)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "gestion_satellites.db")

# Constantes pour les menus déroulants
TYPES_EVENEMENTS = ["Telemetrie", "Alerte", "Commande"]
STATUTS_SATELLITE = ["actif", "maintenance", "critique", "hors_service"]