# TP1 – Introduction à la BI (Partie B)

Ce dossier contient une base SQLite minimale et une application Streamlit pour le tableau de bord.

## Prérequis
- Python 3.10+

## Installation rapide

1) Ouvrir un terminal dans ce dossier.
2) Créer et activer un environnement virtuel.

```zsh
python3 -m venv .venv
source .venv/bin/activate
```

3) Mettre à jour pip et installer les dépendances.

```zsh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4) Initialiser la base (optionnel, l'appli le fera si absente).

```zsh
python db_init.py --reset
```

5) Lancer l'application Streamlit.

```zsh
streamlit run app.py
```

6) Un navigateur s'ouvre sur `http://localhost:8501`. 

## Ce qui est inclus
- `db_init.py` – crée `ventes.db` avec les 3 tables (clients, produits, ventes) + données démo.
- `app.py` – application Streamlit qui affiche:
  - Chiffre d'affaires total et quantité totale vendue,
  - CA par région,
  - Top produits (CA),
  - Évolution mensuelle du CA.
- `requirements.txt` – dépendances Python (pandas, streamlit, altair).

## Notes
- La base est auto-générée au premier lancement. Utilisez `python db_init.py --reset` pour réinitialiser la démo.
- Pour utiliser vos propres données, modifiez `db_init.py` ou alimentez `ventes.db` avec vos inserts.

***

### Dépannage
- Problème de port déjà utilisé: exécutez `streamlit run app.py --server.port 8502`.
- Erreur d'import: vérifiez que l'environnement virtuel est activé (`which python` doit pointer vers `.venv`).
- Si Altair ne s'affiche pas: vérifiez que `pandas`, `altair`, `streamlit` sont bien installés.