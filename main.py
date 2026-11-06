import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk
from commun.widgets import appliquer_style
from dashboard.app_dashboard import AppDashboard
from etudiant_missions.app_missions import AppMissions
from etudiant_satellites.app_satellites import AppSatellites
from etudiant_evenements.app_evenements import AppEvenements
from generateur_gui import GenerateurGUI
from splash import Splash


def main():
    root = tk.Tk()#w principale #w vide
    root.title("SatGuard - Mission Control")
    root.geometry("1400x800")
    root.minsize(1000, 600)
    appliquer_style(root)

    def ouvrir_application():
        splash.destroy()
        notebook = ttk.Notebook(root)#onglets cliquables en haut
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        notebook.add(AppDashboard(notebook),      text="00 Dashboard")
        notebook.add(AppMissions(notebook),       text="01 Missions")
        notebook.add(AppSatellites(notebook),     text="02 Satellites")
        notebook.add(AppEvenements(notebook),     text="03 Événements")
        notebook.add(GenerateurGUI(notebook),     text="04 Simulateur")

    # Écran d'accueil animé : un clic (ou Entrée) ouvre l'application
    splash = Splash(root, ouvrir_application)
    splash.pack(fill="both", expand=True)
    splash.focus_set()

    root.mainloop()


if __name__ == "__main__":
    main()