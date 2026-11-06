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


def main():
    root = tk.Tk()
    root.title("SetGuard - Mission Control")
    root.geometry("1400x800")
    root.minsize(1000, 600)
    appliquer_style(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    notebook.add(AppDashboard(notebook),      text="00 Dashboard")
    notebook.add(AppMissions(notebook),       text="01 Missions")
    notebook.add(AppSatellites(notebook),     text="02 Satellites")
    notebook.add(AppEvenements(notebook),     text="03 Événements")
    notebook.add(GenerateurGUI(notebook),     text="04 Simulateur")

    root.mainloop()

if __name__ == "__main__":
    main()
