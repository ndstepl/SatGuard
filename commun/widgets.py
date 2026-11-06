import tkinter as tk
from tkinter import ttk
from commun import theme


def appliquer_style(root):
    """Applique le thème global à la w."""
    root.configure(bg=theme.COULEURS["fond"])
    style = ttk.Style()
    style.theme_use("clam")
    
    for widget, config in theme.STYLE_CONFIG.items():
        style.configure(widget, **config)
    
    # Supprime les bordures sur les Treeview
    style.configure("Treeview", borderwidth=0, relief="flat")
    style.configure("Treeview.Heading", borderwidth=0, relief="flat")
    style.map("Treeview", background=[("selected", theme.COULEURS["primaire"])])


def creer_titre(parent, texte):#instead of 5 tk.label(..)
    lbl = tk.Label(
        parent, text=texte,
        font=theme.POLICES["titre"],
        fg=theme.COULEURS["primaire"],
        bg=theme.COULEURS["fond"],
        anchor="w"
    )
    lbl.pack(fill="x", pady=(10, 15))
    return lbl


def creer_label(parent, texte, row=0, column=0):
    lbl = ttk.Label(parent, text=texte)
    lbl.grid(row=row, column=column, padx=5, pady=5, sticky="e")
    return lbl


def creer_entry(parent, var, row=0, column=1, width=15):
    ent = ttk.Entry(parent, textvariable=var, width=width)
    ent.grid(row=row, column=column, padx=5, pady=5, sticky="w")
    return ent


def creer_bouton(parent, texte, commande, row=0, column=2, couleur=None):
    btn = ttk.Button(parent, text=texte, command=commande)
    btn.grid(row=row, column=column, padx=10, pady=5)
    return btn


def creer_treeview(parent, colonnes, hauteurs_colonnes, height=15):
    #tableau
    tree = ttk.Treeview(parent, columns=colonnes, show="headings", height=height)
    #Configuration des colonnes
    for col, width in zip(colonnes, hauteurs_colonnes):
        tree.heading(col, text=col.upper())
        tree.column(col, width=width)

    scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    #connecte le tableau et la scrollbar
    tree.configure(yscrollcommand=scroll.set)
  #a utiliser dans la page
    return tree, scroll