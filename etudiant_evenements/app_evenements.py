import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from commun.database import Database
from commun import theme, seed
from commun.widgets import creer_titre, creer_label, creer_bouton, creer_treeview


class AppEvenements(ttk.Frame):
    def __init__(self, master): #notebook dl main.py
        super().__init__(master) #ttk.frame , init frame parent,style..
        seed.initialiser_donnees()
        self.db = Database()
        self.dernier_id_connu = 0
        self._ui()
        self._rafraichir()
        self._surveiller_nouveautes()

    def _ui(self):
        creer_titre(self, "ÉVÉNEMENTS DE TÉLÉMÉTRIE")
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=20, pady=10)

        creer_label(frm, "Satellite :", row=0, column=0)
        self.var_sat = tk.StringVar(value="TOUS")
        self.combo_sat = ttk.Combobox(frm, textvariable=self.var_sat, values=["TOUS"])
        self.combo_sat.grid(row=0, column=1, padx=5)
        self.var_sat.trace_add("write", lambda *_: self._rafraichir())

        creer_label(frm, "Type :", row=0, column=2)
        self.var_type = tk.StringVar(value="TOUS")
        for i, t in enumerate(["TOUS", "Telemetrie", "Alerte", "Commande"]):
            ttk.Radiobutton(frm, text=t, variable=self.var_type, value=t,
                            command=self._rafraichir).grid(row=0, column=3+i, padx=5)

        creer_bouton(frm, "Rafraîchir", self._rafraichir, row=0, column=8)
        creer_bouton(frm, "Supprimer", self._supprimer, row=0, column=9)

        # Légende
        legende = ttk.Frame(self); legende.pack(fill="x", padx=20, pady=5)
        tk.Label(legende, text="● Critique", fg="#ef4444",
                 bg=theme.COULEURS["fond"], font=theme.POLICES["petit"]).pack(side="left", padx=10)
        tk.Label(legende, text="● Attention", fg="#f59e0b",
                 bg=theme.COULEURS["fond"], font=theme.POLICES["petit"]).pack(side="left", padx=10)
        tk.Label(legende, text="● Normal", fg="#e2e8f0",
                 bg=theme.COULEURS["fond"], font=theme.POLICES["petit"]).pack(side="left", padx=10)

        # Tableau
        cols = ("id", "horodatage", "satellite", "type", "message", "batterie", "temperature")
        widths = (60, 150, 120, 100, 350, 80, 80)
        self.tree, scroll = creer_treeview(self, cols, widths, height=20)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

        # TAGS : on colore UNIQUEMENT le texte (foreground), pas le fond
        self.tree.tag_configure('critique', foreground='#ef4444')  # Rouge vif
        self.tree.tag_configure('attention', foreground='#f59e0b')  # Orange
        self.tree.tag_configure('normal',   foreground='#e2e8f0')  # Blanc cassé

    def _surveiller_nouveautes(self): #2s
        try:
            result = self.db.lire("SELECT MAX(id_evenement) as max_id FROM evenements")
            max_id = result[0]["max_id"] if result[0]["max_id"] else 0
            if max_id > self.dernier_id_connu:
                self.dernier_id_connu = max_id
                self._rafraichir()
        except Exception:
            pass
        self.after(2000, self._surveiller_nouveautes)

    def _supprimer(self):
        sel = self.tree.selection()#on recre les lignes sélectionnées par l'utilisateur
        if not sel:
            return messagebox.showwarning("Attention", "Sélectionne un événement")
        self.db.supprimer("DELETE FROM evenements WHERE id_evenement = ?",
                          (self.tree.item(sel[0])["values"][0],))
        self._rafraichir()

    def _rafraichir(self):
        for row in self.tree.get_children():#recuupples lignes du tableau.
            self.tree.delete(row) # vider le tableau avant de le remplir)

        sats = ["TOUS"] + [r["nom"] for r in self.db.lire("SELECT nom FROM satellites")]
        self.combo_sat["values"] = sats

        sat, typ = self.var_sat.get(), self.var_type.get()
        sql = """SELECT e.id_evenement, e.horodatage, s.nom AS satellite,
                        e.type_evenement, e.message, e.batterie, e.temperature
                 FROM evenements e JOIN satellites s ON e.id_satellite = s.id_satellite
                 WHERE 1=1"""
        params = []
        if sat != "TOUS": sql += " AND s.nom = ?"; params.append(sat)
        if typ != "TOUS": sql += " AND e.type_evenement = ?"; params.append(typ)
        sql += " ORDER BY e.horodatage DESC LIMIT 200"

        for r in self.db.lire(sql, tuple(params)):
            valeurs = tuple(r)
            type_evt = valeurs[3]
            batterie = valeurs[5]

            # LOGIQUE DE COLORATION DU TEXTE
            if type_evt == "Alerte" or (batterie is not None and batterie < 30):
                tag = "critique"      # Texte rouge
            elif batterie is not None and batterie < 50:
                tag = "attention"     # Texte orange
            else:
                tag = "normal"        # Texte blanc

            self.tree.insert("", "end", values=valeurs, tags=(tag,)) #Pour chaque ligne de la base :
#Determine le type d'événement et la batterie.
#Choisit un tag (étiquette) pour la couleur : critique (rouge), attention (orange), normal (blanc).
#self.tree.insert() = ajoute une ligne dans le tableau.
##"" = insérer à la racine (pas dans un sous-groupe).
#"end" = à la fin du tableau.
#values=valeurs = les données à afficher.
#tags=(tag,) = la couleur à appliquer