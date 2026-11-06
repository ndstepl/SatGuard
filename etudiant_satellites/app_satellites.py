import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from commun.database import Database, ErreurIntegrite
from commun import theme, seed
from commun.widgets import (creer_titre, creer_label, creer_entry, creer_bouton, creer_treeview)


class AppSatellites(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        seed.initialiser_donnees()
        self.db = Database()
        self.vars = {}
        self._ui()
        self._rafraichir()

    def _ui(self):
        creer_titre(self, "GESTION DES SATELLITES")
        
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=20, pady=10)

        # 1. Mission (Liste déroulante)
        creer_label(frm, "Mission", row=0, column=0)
        missions = [r["nom"] for r in self.db.lire("SELECT nom FROM missions")]
        self.var_mission = tk.StringVar(value=missions[0] if missions else "")
        ttk.Combobox(frm, textvariable=self.var_mission, values=missions, width=12)\
            .grid(row=1, column=0, padx=5, pady=5)

        # 2. Nom (Champ texte)
        creer_label(frm, "Nom", row=0, column=1)
        self.vars["nom"] = tk.StringVar()
        creer_entry(frm, self.vars["nom"], row=1, column=1)

        # 3. Altitude (Champ texte)
        creer_label(frm, "Altitude (m)", row=0, column=2)
        self.vars["alt"] = tk.StringVar()
        creer_entry(frm, self.vars["alt"], row=1, column=2)

        # 4. Vitesse (Champ texte)
        creer_label(frm, "Vitesse (km/s)", row=0, column=3)
        self.vars["vit"] = tk.StringVar()
        creer_entry(frm, self.vars["vit"], row=1, column=3)

        # 5. Inclinaison (Champ texte)
        creer_label(frm, "Inclinaison (°)", row=0, column=4)
        self.vars["inc"] = tk.StringVar()
        creer_entry(frm, self.vars["inc"], row=1, column=4)

        # 6. Statut (Liste déroulante - NOUVEAU)
        creer_label(frm, "Statut", row=0, column=5)
        self.vars["statut"] = tk.StringVar(value="actif")
        ttk.Combobox(frm, textvariable=self.vars["statut"],
                     values=["actif", "maintenance", "critique", "hors_service"],
                     width=12).grid(row=1, column=5, padx=5, pady=5)

        # 7. Boutons d'action
        creer_bouton(frm, "Ajouter", self._ajouter, row=1, column=6)
        creer_bouton(frm, "Modifier", self._modifier, row=1, column=7)
        creer_bouton(frm, "Supprimer", self._supprimer, row=1, column=8)

        # 8. Tableau des satellites
        cols = ("id", "mission", "nom", "altitude", "vitesse", "inclinaison", "statut")
        widths = (60, 120, 130, 100, 100, 100, 100)
        self.tree, scroll = creer_treeview(self, cols, widths, height=18)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

    def _ajouter(self):
        try:
            mission = self.db.lire("SELECT id_mission FROM missions WHERE nom = ?",
                                   (self.var_mission.get(),))
            if not mission:
                return messagebox.showerror("Erreur", "Mission introuvable")
            
            self.db.inserer(
                "INSERT INTO satellites (id_mission, nom, altitude, vitesse, inclinaison, statut) VALUES (?, ?, ?, ?, ?, ?)",
                (mission[0]["id_mission"], self.vars["nom"].get(),
                 float(self.vars["alt"].get()), float(self.vars["vit"].get()),
                 float(self.vars["inc"].get()), self.vars["statut"].get())
            )
            # Vider les champs
            for key in ["nom", "alt", "vit", "inc"]:
                self.vars[key].set("")
            self.vars["statut"].set("actif")
            self._rafraichir()
        except (ErreurIntegrite, ValueError) as e:
            messagebox.showerror("Erreur", str(e))

    def _modifier(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Attention", "Sélectionne un satellite")
        
        values = self.tree.item(sel[0])["values"]
        id_sat, mission_nom, nom, alt, vit, inc, statut = values

        win = tk.Toplevel(self)
        win.title(f"Modifier {nom}")
        win.geometry("350x250")
        win.configure(bg=theme.COULEURS["fond"])

        tk.Label(win, text=f"Satellite : {nom}", font=theme.POLICES["titre"],
                 fg=theme.COULEURS["primaire"], bg=theme.COULEURS["fond"]).pack(pady=15)
        
        # Modifier le statut
        frm_statut = ttk.Frame(win); frm_statut.pack(fill="x", padx=20, pady=5)
        ttk.Label(frm_statut, text="Nouveau statut :").pack(side="left")
        var_statut = tk.StringVar(value=statut)
        ttk.Combobox(frm_statut, textvariable=var_statut,
                     values=["actif", "maintenance", "critique", "hors_service"],
                     width=15).pack(side="left", padx=10)

        # Modifier la mission
        frm_mission = ttk.Frame(win); frm_mission.pack(fill="x", padx=20, pady=5)
        ttk.Label(frm_mission, text="Nouvelle mission :").pack(side="left")
        missions = [r["nom"] for r in self.db.lire("SELECT nom FROM missions")]
        var_mission = tk.StringVar(value=mission_nom)
        ttk.Combobox(frm_mission, textvariable=var_mission,
                     values=missions, width=15).pack(side="left", padx=10)

        def save():
            try:
                new_mission = self.db.lire(
                    "SELECT id_mission FROM missions WHERE nom = ?", (var_mission.get(),))
                if not new_mission:
                    return messagebox.showerror("Erreur", "Mission introuvable")
                
                self.db.ecrire(
                    "UPDATE satellites SET id_mission = ?, statut = ? WHERE id_satellite = ?",
                    (new_mission[0]["id_mission"], var_statut.get(), id_sat)
                )
                self._rafraichir()
                win.destroy()
                messagebox.showinfo("Succès", f"Satellite {nom} mis à jour")
            except ErreurIntegrite as e:
                messagebox.showerror("Erreur", str(e))

        ttk.Button(win, text="Enregistrer", command=save).pack(pady=20)

    def _supprimer(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Attention", "Sélectionne un satellite")
        
        id_s = self.tree.item(sel[0])["values"][0]
        self.db.supprimer("DELETE FROM satellites WHERE id_satellite = ?", (id_s,))
        self._rafraichir()

    def _rafraichir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for r in self.db.lire(
            "SELECT s.id_satellite, m.nom AS mission, s.nom, s.altitude, s.vitesse, s.inclinaison, s.statut "
            "FROM satellites s JOIN missions m ON s.id_mission = m.id_mission"
        ):
            self.tree.insert("", "end", values=tuple(r))