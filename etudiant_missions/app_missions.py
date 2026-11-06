import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from commun.database import Database, ErreurIntegrite
from commun import theme, seed
from commun.widgets import creer_titre, creer_label, creer_entry, creer_bouton, creer_treeview

class AppMissions(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        seed.initialiser_donnees()
        self.db = Database()
        self.vars = {}
        self._ui()
        self._rafraichir()

    def _ui(self):
        creer_titre(self, "GESTION DES MISSIONS")
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=20, pady=10)

        champs_texte = [("Nom", "nom"), ("Agence", "agence"), ("Date (AAAA-MM-JJ)", "date")]
        for i, (label, key) in enumerate(champs_texte):
            creer_label(frm, label, row=0, column=i)
            v = tk.StringVar()
            self.vars[key] = v
            creer_entry(frm, v, row=1, column=i)

        creer_label(frm, "Statut", row=0, column=len(champs_texte))
        self.vars["statut"] = tk.StringVar(value="actif")
        ttk.Combobox(frm, textvariable=self.vars["statut"],
                     values=["actif", "terminé", "en_cours", "annulé"], width=12
        ).grid(row=1, column=len(champs_texte), padx=5, pady=5)

        creer_label(frm, "Objectif", row=0, column=len(champs_texte)+1)
        self.vars["objectif"] = tk.StringVar(value="Observation terrestre")
        ttk.Combobox(frm, textvariable=self.vars["objectif"],
                     values=["Observation terrestre", "Internet global", "Exploration martienne",
                             "Navigation GPS", "Recherche scientifique", "Télécommunications"], width=15
        ).grid(row=1, column=len(champs_texte)+1, padx=5, pady=5)

        creer_bouton(frm, "Ajouter", self._ajouter, row=1, column=len(champs_texte)+2)
        creer_bouton(frm, "Supprimer", self._supprimer, row=1, column=len(champs_texte)+3)

        cols = ("id", "nom", "agence", "date", "statut", "objectif")
        widths = (60, 150, 120, 120, 120, 250)
        self.tree, scroll = creer_treeview(self, cols, widths, height=18)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

    def _ajouter(self):
        # 1. Validation des champs vides
        for key in ["nom", "agence", "date"]:
            if not self.vars[key].get().strip():
                return messagebox.showwarning("Champ vide", f"Le champ '{key}' est obligatoire.")

        # 2. Validation stricte de la date
        date_str = self.vars["date"].get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return messagebox.showerror("Date invalide", "Format attendu : AAAA-MM-JJ (ex: 2026-10-26).\nLes mois vont de 01 à 12, les jours de 01 à 31.")

        # 3. Insertion
        try:
            self.db.inserer(
                "INSERT INTO missions (nom, agence, date_lancement, statut, objectif) VALUES (?, ?, ?, ?, ?)",
                (self.vars["nom"].get(), self.vars["agence"].get(), date_str,
                 self.vars["statut"].get(), self.vars["objectif"].get())
            )
            for v in self.vars.values(): v.set("")
            self.vars["statut"].set("actif")
            self.vars["objectif"].set("Observation terrestre")
            self._rafraichir()
        except ErreurIntegrite as e:
            messagebox.showerror("Erreur", f"Doublon ou erreur : {str(e)}")

    def _supprimer(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Attention", "Sélectionne une mission")
        id_m = self.tree.item(sel[0])["values"][0]
        self.db.supprimer("DELETE FROM missions WHERE id_mission = ?", (id_m,))
        self._rafraichir()

    def _rafraichir(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for r in self.db.lire("SELECT * FROM missions"):
            self.tree.insert("", "end", values=tuple(r))