# 🤖 Chatbot de révision — recherche dans tes fiches PDF

Un assistant en ligne de commande qui **fouille tes fiches PDF** de ce dossier et te renvoie
les passages les plus pertinents, **avec le nom du fichier et le numéro de page**. 100% local et privé.

## Installation (une seule fois)

1. Installe Python 3 (si ce n'est pas déjà fait) : https://www.python.org/downloads/
   ⚠️ Coche « Add Python to PATH » pendant l'installation.
2. Ouvre un terminal **dans ce dossier** et tape :

```bash
pip install -r requirements.txt
```

## Utilisation

Toujours dans ce dossier :

```bash
python chatbot_revision.py
```

Puis pose tes questions, par exemple :
- `c'est quoi le surapprentissage ?`
- `différence entre régression linéaire et logistique`
- `comment gérer les valeurs manquantes ?`

Tape `q` puis Entrée pour quitter.

> Si tu ajoutes / modifies des PDF dans le dossier, l'index se reconstruit tout seul.
> Pour forcer : `python chatbot_revision.py --rebuild`

## Les deux moteurs de recherche

| Moteur | Avantage | Comment l'activer |
|---|---|---|
| **TF-IDF** (par défaut) | Marche immédiatement, rapide, mots-clés | rien à faire |
| **Sémantique** (recommandé) | Comprend le **sens** (ex. « surapprentissage » = « overfitting ») | `pip install sentence-transformers` |

Une fois `sentence-transformers` installé, relance le programme : il bascule automatiquement
en mode sémantique (le 1er lancement télécharge un petit modèle, ~120 Mo, ensuite hors-ligne).

## Comment ça marche (pour le CV / l'entretien)

C'est un mini-système **RAG** (Retrieval-Augmented Generation), brique « retrieval » :
1. **Extraction** : le texte de chaque PDF est lu page par page (`pypdf`).
2. **Découpage** : le texte est coupé en passages de ~110 mots avec chevauchement.
3. **Vectorisation** : chaque passage devient un vecteur (TF-IDF, ou embeddings sémantiques).
4. **Recherche** : ta question est vectorisée, puis comparée à tous les passages par
   **similarité cosinus** ; les meilleurs sont renvoyés avec leur source.

Pour aller plus loin, on pourrait brancher un LLM (local via Ollama, ou API) sur ces passages
pour qu'il **rédige** une réponse en langage naturel — c'est l'étape « generation » du RAG.
