#IA INVOLVMENT

Suivi intelligent de l’attention des apprenants en temps réel à l’aide de la vision par ordinateur et de l’audio.

##Fonctionnalités

- Détection du visage, regard, tête penchée
- Détection des yeux fermés / somnolence
- Analyse du volume sonore ambiant
- Synthèse vocale locale pour les alertes
- Fonctionne entièrement hors ligne

##Structure du projet

- `camera/` → Détection visuelle
- `audio/` → Analyse micro
- `interface/` → (à venir)
- `data/` → Fichiers de score, exports
- `docs/` → Cahier des charges, diagrammes
- `demo/` → Vidéo de démonstration

##Lancer le projet

```bash
python camera/face.detected.py
