# -*- coding: utf-8 -*-
"""
Carrousel LinkedIn (carre 1:1, 6 pages) — style repris du carrousel "Coupe du Monde".
Charte : fond #0E1412, accent or #E9B03B, vert #2ECC71, cartes #141D18.
"""
import os, json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures_dark")
res = json.load(open(os.path.join(BASE, "resultats.json"), encoding="utf-8"))

# ---- Charte ----
FOND  = HexColor("#0E1412")
SURF  = HexColor("#141D18")
SURF2 = HexColor("#18231D")
OR    = HexColor("#E9B03B")
VERT  = HexColor("#2ECC71")
BLANC = HexColor("#F4F6F5")
GRIS  = HexColor("#9AA5A0")
GRIS2 = HexColor("#7C857F")

S = 518.4                       # cote du carre (comme le fichier source)
M = 40                          # marge
W = S
rl, rf = res["resultats"]["Regression logistique"], res["resultats"]["Random Forest"]
best = res["meilleur_modele"]

c = canvas.Canvas(os.path.join(BASE, "Carrousel_LinkedIn_Prediction_Foot.pdf"), pagesize=(S, S))

# ---------- helpers ----------
def fond():
    c.setFillColor(FOND); c.rect(0, 0, S, S, fill=1, stroke=0)

def logo(x=S-M-46, y=S-M-30):
    """Petit logo 'barres' dore, comme la source."""
    c.setFillColor(OR)
    hs = [10, 16, 22, 28, 20]
    for i, h in enumerate(hs):
        c.roundRect(x + i*10, y, 6, h, 2, fill=1, stroke=0)

def pill(x, y, txt, fg, bg, font="Helvetica-Bold", size=10, pad=10, h=22):
    c.setFont(font, size)
    w = c.stringWidth(txt, font, size) + 2*pad
    c.setFillColor(bg); c.roundRect(x, y, w, h, h/2, fill=1, stroke=0)
    c.setFillColor(fg); c.drawString(x+pad, y + (h-size)/2 + 1, txt)
    return w

def footer(n):
    c.setFillColor(GRIS2); c.setFont("Helvetica", 9)
    c.drawString(M, M-14, "Lucien Nzeutom")
    c.setFillColor(OR); c.setFont("Helvetica-Bold", 9)
    c.drawRightString(S-M, M-14, f"{n}/6")

def wrap(txt, font, size, maxw):
    c.setFont(font, size)
    out, line = [], ""
    for word in txt.split():
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= maxw:
            line = test
        else:
            out.append(line); line = word
    if line: out.append(line)
    return out

def para(x, y, txt, font, size, color, maxw, lead, align="left"):
    c.setFillColor(color)
    for ln in wrap(txt, font, size, maxw):
        if align == "left":
            c.setFont(font, size); c.drawString(x, y, ln)
        elif align == "center":
            c.setFont(font, size); c.drawCentredString(x, y, ln)
        y -= lead
    return y

def titre(x, y, lignes, size=30, color=BLANC, lead=34):
    c.setFillColor(color); c.setFont("Helvetica-Bold", size)
    for ln in lignes:
        c.drawString(x, y, ln); y -= lead
    return y

def img_fit(path, x, y, maxw, maxh):
    iw, ih = PILImage.open(path).size
    r = min(maxw/iw, maxh/ih)
    w, h = iw*r, ih*r
    c.drawImage(ImageReader(path), x + (maxw-w)/2, y, width=w, height=h, mask="auto")
    return h

# ====================================================================== PAGE 1 — COUVERTURE
fond(); logo()
pill(M, S-M-24, "PROJET DATA · MACHINE LEARNING", OR, SURF2, size=10)
y = S-150
y = titre(M, y, ["Prédire un match", "de foot avant", "le coup d’envoi ?"], size=34, lead=40)
# soulignement dore
c.setFillColor(OR); c.roundRect(M, y+8, 70, 5, 2, fill=1, stroke=0)
y -= 18
y = para(M, y, "J’ai comparé 3 modèles de machine learning sur 1 900 matchs de "
               "Premier League — sans jamais tricher avec les stats du match.",
         "Helvetica", 13.5, GRIS, S-2*M, 20)
y -= 16
wp = pill(M, y-6, "Python + scikit-learn", FOND, VERT, size=10)
pill(M+wp+8, y-6, "Données Premier League", BLANC, SURF2, size=10)
y -= 44
c.setFillColor(OR); c.setFont("Helvetica-Bold", 12)
c.drawString(M, y, "ce que prédit (vraiment) la data  ➜")
footer(1); c.showPage()

# ====================================================================== PAGE 2 — METHODE
fond(); logo()
c.setFillColor(OR); c.setFont("Helvetica-Bold", 12); c.drawString(M, S-M-18, "LA MÉTHODE")
y = titre(M, S-M-52, ["Prédire sans tricher", "avec le futur."], size=27, lead=32)
y -= 8
# carte 1
ch = 118
c.setFillColor(SURF); c.roundRect(M, y-ch, S-2*M, ch, 12, fill=1, stroke=0)
c.setFillColor(BLANC); c.setFont("Helvetica-Bold", 14); c.drawString(M+18, y-30, "Le piège — la fuite de données")
para(M+18, y-52, "Utiliser les tirs ou les buts du match pour prédire son résultat, "
                 "c’est tricher : ces chiffres n’existent qu’une fois le match joué.",
     "Helvetica", 12, GRIS, S-2*M-36, 18)
y -= ch + 18
# carte 2
ch2 = 130
c.setFillColor(SURF); c.roundRect(M, y-ch2, S-2*M, ch2, 12, fill=1, stroke=0)
c.setFillColor(VERT); c.setFont("Helvetica-Bold", 14); c.drawString(M+18, y-30, "La parade — la forme récente")
para(M+18, y-52, "Toutes les variables sont calculées sur les 5 derniers matchs de chaque "
                 "équipe (buts, tirs cadrés, points...), donc connues AVANT le coup d’envoi. "
                 "21 variables, zéro fuite.",
     "Helvetica", 12, GRIS, S-2*M-36, 18)
y -= ch2 + 26
c.setFillColor(OR); c.setFont("Helvetica-BoldOblique", 12.5)
for ln in wrap("Un modèle honnête se teste sur le futur, jamais sur des infos "
               "qu’il n’aurait pas le jour du match.", "Helvetica-BoldOblique", 12.5, S-2*M):
    c.drawString(M, y, ln); y -= 18
footer(2); c.showPage()

# ====================================================================== PAGE 3 — RESULTATS
fond(); logo()
c.setFillColor(OR); c.setFont("Helvetica-Bold", 13); c.drawString(M, S-M-18, "01")
c.setFillColor(GRIS); c.setFont("Helvetica-Bold", 12); c.drawString(M+22, S-M-18, "LES RÉSULTATS")
titre(M, S-M-50, ["Random Forest l’emporte", "de justesse."], size=24, lead=29)
h = img_fit(os.path.join(FIG, "comparaison.png"), M, 150, S-2*M, 215)
y = 132
c.setFillColor(OR); c.setFont("Helvetica-Bold", 13)
y = para(M, y, "60% de bons pronostics, contre 57% pour un réflexe naïf.", "Helvetica-Bold", 13, OR, S-2*M, 19)
para(M, y-2, "Mieux que le hasard, mais le football garde sa part d’imprévu — "
             "et c’est tant mieux. Un penalty, un carton rouge… restent imprévisibles.",
     "Helvetica", 11.5, GRIS, S-2*M, 17)
footer(3); c.showPage()

# ====================================================================== PAGE 4 — IMPORTANCE
fond(); logo()
c.setFillColor(OR); c.setFont("Helvetica-Bold", 13); c.drawString(M, S-M-18, "02")
c.setFillColor(GRIS); c.setFont("Helvetica-Bold", 12); c.drawString(M+22, S-M-18, "CE QUI COMPTE")
titre(M, S-M-50, ["C’est l’écart de forme", "qui parle."], size=24, lead=29)
img_fit(os.path.join(FIG, "importance.png"), M, 150, S-2*M, 210)
y = 128
para(M, y, "Le modèle a appris seul que la DIFFÉRENCE de dynamique entre les deux "
           "équipes (écart de points et de buts récents) pèse plus que la forme "
           "d’une seule équipe prise isolément.",
     "Helvetica", 12, GRIS, S-2*M, 18)
footer(4); c.showPage()

# ====================================================================== PAGE 5 — KMEANS
fond(); logo()
c.setFillColor(OR); c.setFont("Helvetica-Bold", 13); c.drawString(M, S-M-18, "03")
c.setFillColor(GRIS); c.setFont("Helvetica-Bold", 12); c.drawString(M+22, S-M-18, "BONUS NON SUPERVISÉ")
titre(M, S-M-50, ["La data dessine", "4 styles d’équipes."], size=24, lead=29)
img_fit(os.path.join(FIG, "clusters.png"), M, 150, S-2*M, 215)
y = 128
para(M, y, "Sans jamais lui donner le classement, un KMeans regroupe les équipes en "
           "4 familles cohérentes — des cadors aux équipes qui luttent pour le maintien. "
           "Preuve que les données portent une vraie structure.",
     "Helvetica", 12, GRIS, S-2*M, 18)
footer(5); c.showPage()

# ====================================================================== PAGE 6 — LIMITES + CTA
fond(); logo()
c.setFillColor(OR); c.setFont("Helvetica-Bold", 12); c.drawString(M, S-M-18, "EN TOUTE HONNÊTETÉ")
y = titre(M, S-M-52, ["Une démarche,", "pas une boule de cristal."], size=24, lead=29)
y -= 6
limites = [
    "Une seule ligue, 5 saisons : à généraliser avec prudence.",
    "Blessures, fatigue, compositions… ignorées faute de données.",
    "AUC ~0,65 : un résultat honnête, pas un système de paris.",
]
for lim in limites:
    c.setFillColor(OR); c.setFont("Helvetica-Bold", 12); c.drawString(M, y, "•")
    yy = para(M+16, y, lim, "Helvetica", 12, GRIS, S-2*M-16, 17)
    y = yy - 8
y -= 6
# encart conclusion
bh = 96
c.setFillColor(SURF); c.roundRect(M, y-bh, S-2*M, bh, 12, fill=1, stroke=0)
c.setFillColor(OR); c.roundRect(M, y-bh, 5, bh, 2, fill=1, stroke=0)
c.setFillColor(BLANC); c.setFont("Helvetica-Bold", 13); c.drawString(M+20, y-26, "Ce que ce projet démontre")
para(M+20, y-46, "Une chaîne complète et reproductible : données réelles, "
                 "features sans fuite, comparaison de modèles, clustering, "
                 "et un modèle exporté prêt à prédire de nouveaux matchs.",
     "Helvetica", 11, GRIS, S-2*M-36, 16)
y -= bh + 30
c.setFillColor(OR); c.setFont("Helvetica-Bold", 13)
c.drawString(M, y, "Le code + le rapport complet sont dispos.  On en parle ?  ➜")
footer(6); c.showPage()

c.save()
print("Carrousel genere : Carrousel_LinkedIn_Prediction_Foot.pdf")
