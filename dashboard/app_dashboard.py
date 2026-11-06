import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from datetime import datetime 
from commun.database import Database
from commun import theme, seed
from commun.widgets import creer_titre


class AppDashboard(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        seed.initialiser_donnees()#Vérify si la bd existe, sinn cree et remp
        self.db = Database() #conn open
       
       # self.barre_widgets = {}   # lcache lles barres
        #self.alertes_cache = []   # l Cache dles alertes //amelioration:)
        self._ui()
        self._rafraichir()
        self.after(3000, self._auto_refresh)
        
     # La Construction de l ui(the big 2)
    def _ui(self):
        creer_titre(self, "DASHBORD — MISSION CONTROL")

        footer = tk.Frame(self, bg=theme.COULEURS["fond"])
        footer.pack(side="bottom", fill="x")

        tk.Frame(footer, bg=theme.COULEURS["bordure"], height=1).pack(fill="x", padx=20)

        tk.Label(
            footer,
            text=f"© {datetime.now().year} f_i_c— Mission Control. Tous droits reservees.",
            font=("Segoe UI", 8),
            fg=theme.COULEURS["texte_mute"],
            bg=theme.COULEURS["fond"]
         ).pack(pady=6)

        # === LIGNE 1 : 6 CARTES KPI ===
        self.kpi_frame = ttk.Frame(self)
        self.kpi_frame.pack(fill="x", padx=20, pady=10)

        self.kpis = {}
        kpi_labels = [
            ("missions",   "MISSIONS EN COURS",  "SUR {} MISSIONS",    theme.COULEURS["primaire"]),
            ("actifs",     "SATELLITES ACTIFS",  "SUR {} SATELLITES",  theme.COULEURS["succes"]),
            ("panne",      "EN PANNE",           "INTERVENTION REQUISE", theme.COULEURS["danger"]),
            ("critique",   "SANTÉ CRITIQUE",     "DÉGRADÉ(S)",         theme.COULEURS["warning"]),
            ("alertes",    "ALERTES",            "À TRAITER",          "#f97316"),
            ("batterie",   "BATTERIE MOYENNE",   "DERNIÈRES MESURES",  theme.COULEURS["succes"]),
        ]

        for i, (key, titre, sous_titre, couleur) in enumerate(kpi_labels):
            carte = ttk.Frame(self.kpi_frame, relief="flat", borderwidth=0)
            carte.configure(style="TFrame")
            carte.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            self.kpi_frame.columnconfigure(i, weight=1)

            # Fond coloré pour la carte
            carte_bg = tk.Frame(carte, bg=theme.COULEURS["fond_clair"],
                               highlightthickness=0, bd=0)
            carte_bg.pack(fill="both", expand=True, padx=2, pady=2)

            tk.Label(carte_bg, text=titre, font=("Segoe UI", 8, "bold"),
                     fg=theme.COULEURS["texte_mute"], bg=theme.COULEURS["fond_clair"]
            ).pack(pady=(8, 2))

            valeur_lbl = tk.Label(carte_bg, text="0", font=("Segoe UI", 28, "bold"),
                                  fg=couleur, bg=theme.COULEURS["fond_clair"])
            valeur_lbl.pack()

            sous_lbl = tk.Label(carte_bg, text=sous_titre, font=("Segoe UI", 7),
                                fg=theme.COULEURS["texte_mute"], bg=theme.COULEURS["fond_clair"])
            sous_lbl.pack(pady=(2, 8))

            self.kpis[key] = {"valeur": valeur_lbl, "sous": sous_lbl, "couleur": couleur}

        # === LIGNE 2 : GRAPHIQUE + ALERTES ===
        bas = ttk.Frame(self)
        bas.pack(fill="both", expand=True, padx=20, pady=10)

        # --- GAUCHE : Graphique barres ---
        # Remplacement du ttk.LabelFrame (bordure blanche) par un tk.Frame sombre
        gauche = tk.Frame(bas, bg=theme.COULEURS["fond_clair"],
                          highlightbackground=theme.COULEURS["bordure"],
                          highlightthickness=1)
        gauche.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Titre de la section (remplace le text= du LabelFrame)
        tk.Label(gauche, text="ÉVÉNEMENTS PAR TYPE",
                 font=("Segoe UI", 10, "bold"),
                 fg=theme.COULEURS["primaire"],
                 bg=theme.COULEURS["fond_clair"],
                 anchor="w").pack(fill="x", padx=15, pady=(10, 5))

        # Ligne séparatrice
        tk.Frame(gauche, bg=theme.COULEURS["bordure"], height=1).pack(fill="x", padx=15)

        self.barres_container = tk.Frame(gauche, bg=theme.COULEURS["fond_clair"])
        self.barres_container.pack(fill="both", expand=True, padx=15, pady=10)

        # --- DROITE : Dernières alertes ---
        # Remplacement du ttk.LabelFrame (bordure blanche) par un tk.Frame sombre
        droite = tk.Frame(bas, bg=theme.COULEURS["fond_clair"],
                          highlightbackground=theme.COULEURS["bordure"],
                          highlightthickness=1)
        droite.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(droite, text="DERNIÈRES ALERTES",
                 font=("Segoe UI", 10, "bold"),
                 fg="#ef4444",
                 bg=theme.COULEURS["fond_clair"],
                 anchor="w").pack(fill="x", padx=15, pady=(10, 5))

        tk.Frame(droite, bg=theme.COULEURS["bordure"], height=1).pack(fill="x", padx=15)

        self.alertes_canvas = tk.Canvas(droite, bg=theme.COULEURS["fond_clair"],
                                        highlightthickness=0, bd=0)
        self.alertes_scroll = ttk.Scrollbar(droite, orient="vertical",
                                            command=self.alertes_canvas.yview)
        self.alertes_inner = tk.Frame(self.alertes_canvas, bg=theme.COULEURS["fond_clair"])

        self.alertes_inner.bind(
            "<Configure>",
            lambda e: self.alertes_canvas.configure(scrollregion=self.alertes_canvas.bbox("all"))
        )
        self.alertes_canvas.create_window((0, 0), window=self.alertes_inner, anchor="nw")
        self.alertes_canvas.configure(yscrollcommand=self.alertes_scroll.set)

        self.alertes_canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=10)
        self.alertes_scroll.pack(side="right", fill="y", pady=10)

    def _rafraichir(self):
        try:
            self._maj_kpis()
            self._maj_graphique()
            self._maj_alertes()
        except Exception as e:# # Si erreur , on l'affiche dans la consolelieu deplanter l'app
            print(f"Erreur dashboard : {e}")

    def _maj_kpis(self):
        total_missions = self.db.lire("SELECT COUNT(*) as c FROM missions")[0]["c"]#compter les missions
        stats_sat = {r["statut"]: r["c"] for r in self.db.lire(#cpt satellites par statut 
            "SELECT statut, COUNT(*) as c FROM satellites GROUP BY statut"# transforme le res en dictionnaire Python
        )}
        total_sats = sum(stats_sat.values())#calc stats
        actifs = stats_sat.get("actif", 0)## .get évite une erreur si la clé n'existe pas (retourne 0 par défa
        panne = stats_sat.get("hors_service", 0)
        critique = stats_sat.get("critique", 0) + stats_sat.get("maintenance", 0)

        nb_alertes = self.db.lire(
            "SELECT COUNT(*) as c FROM evenements WHERE type_evenement = 'Alerte' OR batterie < 30"
        )[0]["c"]

        batt_moy = self.db.lire(
            "SELECT AVG(batterie) as m FROM evenements ORDER BY id_evenement DESC LIMIT 50"
        )[0]["m"]
        batt_moy = round(batt_moy, 1) if batt_moy else 0
          #MISE À JOUR DE L'INTERFACE ,uses self.kpi(ui)
        self._set_kpi("missions", total_missions, f"SUR {total_missions} MISSIONS")
        self._set_kpi("actifs", actifs, f"SUR {total_sats} SATELLITES")
        self._set_kpi("panne", panne, "INTERVENTION REQUISE")
        self._set_kpi("critique", critique, "DÉGRADÉ(S)")
        self._set_kpi("alertes", nb_alertes, "À TRAITER")
        self._set_kpi("batterie", f"{batt_moy} %", "DERNIÈRES MESURES")

    def _set_kpi(self, key, valeur, sous_titre):
        self.kpis[key]["valeur"].config(text=str(valeur))
        self.kpis[key]["sous"].config(text=sous_titre)

    def _maj_graphique(self):#barres
        stats = {r["type_evenement"]: r["c"] for r in self.db.lire(#compte les events par type
            "SELECT type_evenement, COUNT(*) as c FROM evenements GROUP BY type_evenement"
        )}
        total = sum(stats.values())
        if total == 0:
            return
       #dict
        couleurs = {
            "Telemetrie": "#38bdf8",
            "Alerte":     "#f87171",
            "Commande":   "#efe33e",
        }
        # winfo_children() récupère la liste de tous les widgets (lignes) dans le container
        for w in self.barres_container.winfo_children():
            w.destroy()
         #On cherche la valeur la plus haute pour que la barre la plus longue prenne 100% de l'espace
        max_val = max(stats.values()) if stats else 1
         #trie les types du plus grand au plus petit
        for i, (typ, count) in enumerate(sorted(stats.items(), key=lambda x: -x[1])):
            ligne = ttk.Frame(self.barres_container)#creation ligne
            ligne.pack(fill="x", pady=8)
            
            tk.Label(ligne, text=typ.upper(), width=12, anchor="w",
                     font=("Segoe UI", 9, "bold"),
                     fg=theme.COULEURS["texte"], bg=theme.COULEURS["fond_clair"]
            ).pack(side="left")
             ## Calcul de la largeur en pixels 300
            largeur_max = 300
            largeur = int((count / max_val) * largeur_max) if max_val > 0 else 0

            barre_bg = tk.Frame(ligne, bg=theme.COULEURS["fond"], height=24, bd=0)
            barre_bg.pack(side="left", fill="x", expand=True, padx=10)

            barre = tk.Frame(barre_bg, bg=couleurs.get(typ, "#888"), height=24, width=largeur, bd=0)
            barre.pack(side="left", fill="y")
            barre.pack_propagate(False)# empêche le Frame de rétrécir 

            tk.Label(ligne, text=str(count), width=5,#Label du nombre
                     font=("Segoe UI", 9, "bold"),
                     fg=theme.COULEURS["texte"], bg=theme.COULEURS["fond_clair"]
            ).pack(side="left")

    def _maj_alertes(self):
        alertes = self.db.lire(
            """SELECT e.horodatage, s.nom, e.type_evenement, e.message, e.batterie
               FROM evenements e
               JOIN satellites s ON e.id_satellite = s.id_satellite
               WHERE e.type_evenement = 'Alerte' OR e.batterie < 30
               ORDER BY e.id_evenement DESC
               LIMIT 10"""
        )

        for w in self.alertes_inner.winfo_children():
            w.destroy()

        if not alertes:
            tk.Label(self.alertes_inner, text="Aucune alerte récente ",
                     fg=theme.COULEURS["succes"], bg=theme.COULEURS["fond_clair"],
                     font=("Segoe UI", 10)).pack(pady=30)
            return

        for a in alertes:
            horo = a["horodatage"].split(" ")[1] if " " in a["horodatage"] else a["horodatage"]
            batt = a["batterie"]
            texte = f"{horo}  {a['nom']}  {a['message']} ({batt} %)"

            ligne = tk.Frame(self.alertes_inner, bg=theme.COULEURS["fond_clair"], bd=0)
            ligne.pack(fill="x", pady=3)

            tk.Label(ligne, text="●", fg="#f87171",
                     bg=theme.COULEURS["fond_clair"], font=("Segoe UI", 8)
            ).pack(side="left", padx=5)

            tk.Label(ligne, text=texte, fg="#fca5a5",
                     bg=theme.COULEURS["fond_clair"], font=("Consolas", 9),
                     anchor="w"
            ).pack(side="left", fill="x", expand=True)

    def _auto_refresh(self):
        self._rafraichir()
        self.after(2000, self._auto_refresh)