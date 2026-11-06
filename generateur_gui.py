import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random, threading, time #1if not identique2 lancer le sim dans unthreadexec parallele 

from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox
from commun.database import Database  #conn 3
from commun import theme, seed
from commun.widgets import creer_titre, creer_treeview

TYPES = {#genere lesphrases
    "Telemetrie": ["Altitude {alt} km, vitesse {vit} km/s", "Données télémétriques normales"],
    "Alerte":     ["Niveau batterie critique", "Anomalie panneau solaire", "Déviation orbitale"],
    "Commande":   ["Ajustement orbital effectué", "Calibration capteurs", "Mode safe activé"],
}

class GenerateurGUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        seed.initialiser_donnees()
        self.db = Database()
        self.running = False#interupter
        self.compteur = 0 #comp succes
        self._ui()

    def _ui(self):
        creer_titre(self, "SIMULATEUR DE TÉLÉMÉTRIE")
        ctrl = ttk.Frame(self)#boutoon/labels sur mm ligne
        ctrl.pack(fill="x", padx=20, pady=10)

        self.status_lbl = tk.Label(ctrl, text=" Arrêté", font=theme.POLICES["normal"],
                                   fg=theme.COULEURS["danger"], bg=theme.COULEURS["fond"])
        self.status_lbl.pack(side="left", padx=10)

        self.btn = ttk.Button(ctrl, text="▶ Démarrer la simulation", command=self._toggle)
        self.btn.pack(side="left", padx=10)

        self.compteur_lbl = tk.Label(ctrl, text="Événements générés : 0",
                                     font=theme.POLICES["normal"],
                                     fg=theme.COULEURS["texte"], bg=theme.COULEURS["fond"])
        self.compteur_lbl.pack(side="right", padx=10)

        cols = ("horodatage", "satellite", "type", "message", "batterie", "temperature")
        widths = (150, 120, 100, 300, 80, 80)
        self.tree, scroll = creer_treeview(self, cols, widths, height=20)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

    def _toggle(self):#le Start/Stop
        if self.running: #siil tourne des depart
            self.running = False#stop
            self.btn.config(text="-> Démarrer la simulation")
            self.status_lbl.config(text=" Arrêté", fg=theme.COULEURS["danger"])
        else:#arrete on demarre
            sats = self.db.lire("SELECT COUNT(*) as c FROM satellites")
            if sats[0]["c"] == 0:
                messagebox.showwarning("Attention", "Aucun satellite. Ajoute-en dans l'onglet 02.")
                return#quit on demarrepas

            self.running = True
            self.btn.config(text="⏸ Arrêter la simulation")
            self.status_lbl.config(text="<> En cours...", fg=theme.COULEURS["succes"])
            # Lancement du thread (moteur)deamon
            threading.Thread(target=self._boucle, daemon=True).start()

    def _boucle(self):
        # On relit les satellites à chaque démarrage de boucle, recup 1 time
        sats = self.db.lire("SELECT id_satellite, nom, altitude, vitesse FROM satellites")
        
        while self.running:
            try:#1choix alt
                sat = random.choice(sats)
                typ = random.choice(list(TYPES.keys()))
                msg = random.choice(TYPES[typ]).format(
                    alt=round(sat["altitude"] / 1000, 0), vit=round(sat["vitesse"], 2)
                )
                horo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                batt = round(random.uniform(10, 100), 1)  # Baisse la borne à 10 pour forcer des alertes
                temp = round(random.uniform(-20, 60), 1)

                # Écriture en bd
                self.db.ecrire(
                    "INSERT INTO evenements (id_satellite, horodatage, type_evenement, message, batterie, temperature) VALUES (?, ?, ?, ?, ?, ?)",
                    (sat["id_satellite"], horo, typ, msg, batt, temp)
                )

                self.compteur += 1
                
                # Mise à jour de l'UI via self.after() pour éviter le crash Tkinter
                self.after(0, self._maj_ui, horo, sat["nom"], typ, msg, batt, temp)
                #pause 1s--3s
                time.sleep(random.uniform(1, 3))
            #erreurs pour ne pasplanter l'app   
            except Exception as e:
                print(f"Erreur thread simulation : {e}")
                self.running = False
                self.after(0, lambda: self.status_lbl.config(text=" ERREUR", fg="red"))
                break

    def _maj_ui(self, horo, nom, typ, msg, batt, temp):
        """Mise à jour de l'interface (appelée sur le thread principal)."""
        #Insère la nouvelle ligne tout en haut du tableau (index 0)
        self.tree.insert("", 0, values=(horo, nom, typ, msg, batt, temp))
        if len(self.tree.get_children()) > 50:#si le tableau dépasse 50 lignes, on supprime la dern
            self.tree.delete(self.tree.get_children()[-1]) 
        self.compteur_lbl.config(text=f"Événements générés : {self.compteur}")
        #mj compteur :)