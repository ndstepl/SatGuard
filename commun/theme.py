# Palette "Mission Control" sombre
COULEURS = {
    "fond":        "#070b14",
    "fond_clair":  "#0d1424",
    "primaire":    "#C48A1E",
    "accent":      "#f97316",
    "texte":       "#e8edf7",
    "texte_mute":  "#7d8aa5",
    "bordure":     "#1b2740",
    "succes":      "#3ddc97",
    "danger":      "#ff6b6b",
    "warning":     "#ff8a5c",
}

POLICES = {
    "titre":   ("Segoe UI", 16, "bold"),
    "normal":  ("Segoe UI", 10),
    "petit":   ("Segoe UI", 9),
    "tableau": ("Consolas", 9),
}

# Configuration du style ttk
STYLE_CONFIG = {
    "TFrame":        {"background": COULEURS["fond"]},
    "TLabel":        {"background": COULEURS["fond"],
                      "foreground": COULEURS["texte"],
                      "font": POLICES["normal"]},
    "TLabelFrame":   {"background": COULEURS["fond"],
                      "foreground": COULEURS["primaire"]},
    "TButton":       {"background": COULEURS["primaire"],
                      "foreground": "#ffffff",
                      "font": POLICES["normal"]},
    "TEntry":        {"fieldbackground": COULEURS["fond_clair"],
                      "foreground": COULEURS["texte"],
                      "font": POLICES["normal"]},
    "TCombobox":     {"fieldbackground": COULEURS["fond_clair"],
                      "foreground": COULEURS["texte"],
                      "font": POLICES["normal"]},
    "Treeview":      {"background": COULEURS["fond_clair"],
                      "foreground": COULEURS["texte"],
                      "fieldbackground": COULEURS["fond_clair"],
                      "font": POLICES["tableau"]},
    "Treeview.Heading": {"background": COULEURS["bordure"],
                         "foreground": COULEURS["primaire"],
                         "font": POLICES["normal"]},
}