# -*- coding: utf-8 -*-
"""
==========================================================================================
 CHATBOT DE REVISION — recherche semantique dans tes fiches PDF (100% local & prive)
==========================================================================================
Tu poses une question, le programme fouille tes PDF de revision et te renvoie les
passages les plus pertinents, AVEC le nom du fichier et le numero de page.

Deux moteurs, choisis automatiquement :
  - SEMANTIQUE (recommande) : si la librairie 'sentence-transformers' est installee,
    il comprend le SENS (ex. "surapprentissage" ~ "overfitting").
  - TF-IDF (par defaut) : marche tout de suite avec scikit-learn, base sur les mots-cles.

Lancement :
    python chatbot_revision.py            # construit l'index puis ouvre le chat
    python chatbot_revision.py --rebuild  # force la reconstruction de l'index
==========================================================================================
"""

import os
import re
import sys
import glob
import pickle
import hashlib

import numpy as np
from pypdf import PdfReader

DOSSIER = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(DOSSIER, ".index_cache.pkl")
TOP_K = 5
MOTS_PAR_CHUNK = 110
RECOUVREMENT = 30
MODELE_SEMANTIQUE = "paraphrase-multilingual-MiniLM-L12-v2"

STOPWORDS_FR = [
    "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "elle", "en", "et", "eux",
    "il", "ils", "je", "la", "le", "les", "leur", "lui", "ma", "mais", "me", "meme", "mes",
    "moi", "mon", "ne", "nos", "notre", "nous", "on", "ou", "par", "pas", "pour", "qu", "que",
    "qui", "sa", "se", "ses", "son", "sur", "ta", "te", "tes", "toi", "ton", "tu", "un", "une",
    "vos", "votre", "vous", "est", "sont", "etre", "cela", "comme", "plus", "aussi", "donc",
    "quoi", "comment", "pourquoi", "quel", "quelle", "quels", "quelles", "quand", "combien",
    "entre", "difference", "differences", "ca", "fait", "faire", "sert", "servent", "veut",
    "dire", "explique", "expliquer", "definir", "definition", "exemple", "exemples", "ton",
    "mes", "non", "oui", "tout", "tous", "toute", "toutes", "peux", "peut", "etait", "ete",
]


class C:
    OR = "\033[33m"; VERT = "\033[32m"; GRAS = "\033[1m"
    GRIS = "\033[90m"; CYAN = "\033[36m"; OFF = "\033[0m"


# ==========================================================================================
# 1. EXTRACTION DU TEXTE + DECOUPAGE EN PASSAGES
# ==========================================================================================
def nettoyer(txt):
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{2,}", "\n", txt)
    return txt.strip()


def extraire_passages():
    """Retourne une liste de dicts : {fichier, page, texte}."""
    passages = []
    pdfs = sorted(glob.glob(os.path.join(DOSSIER, "*.pdf")))
    if not pdfs:
        print("Aucun PDF trouve dans :\n  " + DOSSIER)
        sys.exit(1)
    for chemin in pdfs:
        nom = os.path.basename(chemin)
        try:
            lecteur = PdfReader(chemin)
        except Exception as e:
            print("  (!) Impossible de lire " + nom + " : " + str(e))
            continue
        for i, page in enumerate(lecteur.pages, start=1):
            texte = nettoyer(page.extract_text() or "")
            mots = texte.split()
            if len(mots) < 8:
                continue
            pas = MOTS_PAR_CHUNK - RECOUVREMENT
            for d in range(0, len(mots), pas):
                bout = " ".join(mots[d:d + MOTS_PAR_CHUNK]).strip()
                if len(bout) > 40:
                    passages.append({"fichier": nom, "page": i, "texte": bout})
    return passages


def empreinte_pdfs():
    """Signature des PDF (nom+taille+date) pour savoir si l'index doit etre refait."""
    h = hashlib.md5()
    for chemin in sorted(glob.glob(os.path.join(DOSSIER, "*.pdf"))):
        st = os.stat(chemin)
        h.update((os.path.basename(chemin) + "|" + str(st.st_size) + "|" + str(int(st.st_mtime))).encode())
    return h.hexdigest()


# ==========================================================================================
# 2. CONSTRUCTION DE L'INDEX (semantique si possible, sinon TF-IDF)
# ==========================================================================================
def moteur_disponible():
    try:
        import sentence_transformers  # noqa
        return "semantique"
    except Exception:
        return "tfidf"


def construire_index(force=False):
    sig = empreinte_pdfs()
    moteur = moteur_disponible()

    if not force and os.path.exists(CACHE):
        try:
            with open(CACHE, "rb") as f:
                cache = pickle.load(f)
            if cache.get("signature") == sig and cache.get("moteur") == moteur:
                return cache
        except Exception:
            pass

    print(C.GRIS + "Construction de l'index (" + moteur + ")..." + C.OFF)
    passages = extraire_passages()
    textes = [p["texte"] for p in passages]

    if moteur == "semantique":
        from sentence_transformers import SentenceTransformer
        modele = SentenceTransformer(MODELE_SEMANTIQUE)
        vecteurs = modele.encode(textes, normalize_embeddings=True,
                                 show_progress_bar=True, batch_size=64)
        cache = {"moteur": "semantique", "signature": sig, "passages": passages,
                 "vecteurs": np.asarray(vecteurs, dtype="float32"),
                 "modele_nom": MODELE_SEMANTIQUE}
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True,
                               strip_accents="unicode", stop_words=STOPWORDS_FR)
        matrice = vect.fit_transform(textes)
        cache = {"moteur": "tfidf", "signature": sig, "passages": passages,
                 "vectoriseur": vect, "matrice": matrice}

    try:
        with open(CACHE, "wb") as f:
            pickle.dump(cache, f)
    except Exception:
        pass
    print(C.VERT + "Index pret : " + str(len(passages)) + " passages indexes." + C.OFF + "\n")
    return cache


# ==========================================================================================
# 3. RECHERCHE
# ==========================================================================================
_MODELE = {}


def _modele_semantique(nom):
    if nom not in _MODELE:
        from sentence_transformers import SentenceTransformer
        _MODELE[nom] = SentenceTransformer(nom)
    return _MODELE[nom]


def rechercher(cache, question, k=TOP_K):
    if cache["moteur"] == "semantique":
        modele = _modele_semantique(cache["modele_nom"])
        q = modele.encode([question], normalize_embeddings=True)[0].astype("float32")
        scores = cache["vecteurs"] @ q
    else:
        from sklearn.metrics.pairwise import linear_kernel
        q = cache["vectoriseur"].transform([question])
        scores = linear_kernel(q, cache["matrice"]).ravel()

    idx = np.argsort(scores)[::-1][:k]
    return [(cache["passages"][i], float(scores[i])) for i in idx]


# ==========================================================================================
# 4. INTERFACE CHAT (ligne de commande)
# ==========================================================================================
def surligner(texte, question):
    mots = re.findall(r"\w{4,}", question.lower())
    for m in sorted(set(mots), key=len, reverse=True):
        texte = re.sub("(?i)(" + re.escape(m) + ")", C.GRAS + r"\1" + C.OFF, texte)
    return texte


def afficher(resultats, question):
    if not resultats or resultats[0][1] < 0.02:
        print(C.OR + "Aucun passage vraiment pertinent trouve. Reformule ta question ?" + C.OFF + "\n")
        return
    maxi = resultats[0][1]
    print(C.CYAN + C.GRAS + "Voici ce que j'ai trouve dans tes fiches :" + C.OFF + "\n")
    for rang, (p, score) in enumerate(resultats, 1):
        if score < 0.02 or score < 0.25 * maxi:
            continue
        pct = int(round(score / maxi * 100))
        print(C.OR + C.GRAS + "[" + str(rang) + "] " + p["fichier"] + " - page " + str(p["page"]) + C.OFF
              + "   " + C.GRIS + "(pertinence " + str(pct) + "%)" + C.OFF)
        extrait = p["texte"]
        if len(extrait) > 600:
            extrait = extrait[:600] + "..."
        print("    " + surligner(extrait, question).replace("\n", "\n    "))
        print()


def banniere(moteur):
    nom = "SEMANTIQUE (comprend le sens)" if moteur == "semantique" else "TF-IDF (mots-cles)"
    print("=" * 74)
    print("  CHATBOT DE REVISION DATA SCIENCE   ·   moteur : " + nom)
    print("  Pose ta question. Tape 'q' pour quitter.")
    print("=" * 74 + "\n")


def main():
    force = "--rebuild" in sys.argv
    cache = construire_index(force=force)
    banniere(cache["moteur"])
    if cache["moteur"] == "tfidf":
        print(C.GRIS + "Astuce : pour la recherche semantique (synonymes), installe :"
              + "  pip install sentence-transformers" + C.OFF + "\n")
    while True:
        try:
            q = input(C.GRAS + "Ta question > " + C.OFF).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nA bientot !")
            break
        if not q:
            continue
        if q.lower() in {"q", "quit", "exit", "quitter"}:
            print("A bientot !")
            break
        print()
        afficher(rechercher(cache, q), q)


if __name__ == "__main__":
    main()
