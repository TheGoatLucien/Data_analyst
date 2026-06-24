# -*- coding: utf-8 -*-
"""Generation du PDF de synthese (style LinkedIn, pro) avec ReportLab."""
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table,
                                TableStyle, HRFlowable, PageBreak)

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
res = json.load(open(os.path.join(BASE, "resultats.json"), encoding="utf-8"))

BLEU = colors.HexColor("#0A66C2")
BLEU_F = colors.HexColor("#08294A")
ORANGE = colors.HexColor("#F39C12")
VERT = colors.HexColor("#2ECC71")
GRIS = colors.HexColor("#5A6570")
GRIS_C = colors.HexColor("#ECF0F3")

styles = getSampleStyleSheet()
def S(name, **kw):
    return ParagraphStyle(name, parent=styles["Normal"], **kw)

st_titre = S("t", fontName="Helvetica-Bold", fontSize=26, textColor=colors.white, leading=30, alignment=TA_LEFT)
st_sous = S("s", fontName="Helvetica", fontSize=13, textColor=colors.white, leading=18)
st_h = S("h", fontName="Helvetica-Bold", fontSize=15, textColor=BLEU_F, spaceBefore=14, spaceAfter=6)
st_body = S("b", fontName="Helvetica", fontSize=10.5, textColor=colors.HexColor("#222"), leading=16, alignment=TA_JUSTIFY)
st_small = S("sm", fontName="Helvetica-Oblique", fontSize=8.5, textColor=GRIS, leading=12)
st_card_n = S("cn", fontName="Helvetica-Bold", fontSize=22, textColor=BLEU, alignment=TA_CENTER, leading=24)
st_card_l = S("cl", fontName="Helvetica", fontSize=8.5, textColor=GRIS, alignment=TA_CENTER, leading=11)

def bande_couv(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLEU_F)
    canvas.rect(0, A4[1]-7.5*cm, A4[0], 7.5*cm, fill=1, stroke=0)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, A4[1]-7.7*cm, A4[0], 0.2*cm, fill=1, stroke=0)
    canvas.restoreState()

def pied(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2*cm, 1.1*cm, "Lucien Nzeutom — Projet Data Science")
    canvas.drawRightString(A4[0]-2*cm, 1.1*cm, f"Page {doc.page}")
    canvas.setStrokeColor(GRIS_C); canvas.line(2*cm, 1.5*cm, A4[0]-2*cm, 1.5*cm)
    canvas.restoreState()

def couv(canvas, doc): bande_couv(canvas, doc); pied(canvas, doc)

def carte(n, label, coul=BLEU):
    p_n = ParagraphStyle("x", parent=st_card_n, textColor=coul)
    t = Table([[Paragraph(n, p_n)], [Paragraph(label, st_card_l)]], colWidths=[3.9*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRIS_C),
        ("BOX", (0,0), (-1,-1), 0.5, colors.white),
        ("TOPPADDING", (0,0), (-1,0), 10), ("BOTTOMPADDING", (0,1), (-1,1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    return t

def img(path, w):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    return Image(path, width=w, height=w*ih/iw)

el = []
# ----- COUVERTURE -----
el.append(Spacer(1, 1.2*cm))
el.append(Paragraph("Prédire le résultat d’un match", st_titre))
el.append(Paragraph("de football", st_titre))
el.append(Spacer(1, 0.3*cm))
el.append(Paragraph("Machine learning supervisé &amp; non supervisé — Premier League", st_sous))
el.append(Spacer(1, 2.9*cm))

intro = ("<b>Le défi.</b> Peut-on, <b>avant le coup d’envoi</b>, estimer la probabilité qu’une "
         "équipe gagne à domicile, en se basant uniquement sur la dynamique récente des deux équipes ? "
         "J’ai comparé deux modèles supervisés (régression logistique et random forest) et exploré les "
         "styles de jeu via un modèle non supervisé (KMeans), sur "
         f"<b>{res['n_matchs']} matchs</b> de Premier League ({res['n_saisons']} saisons).")
el.append(Paragraph(intro, st_body))
el.append(Spacer(1, 0.5*cm))

cartes = Table([[
    carte(str(res["n_matchs"]), "matchs analysés"),
    carte(f"{res['n_features']}", "variables pré-match"),
    carte(f"{int(res['resultats'][res['meilleur_modele']]['auc']*100)}%", "AUC (meilleur modèle)", VERT),
    carte("3", "modèles comparés", ORANGE),
]], colWidths=[4.2*cm]*4)
cartes.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
el.append(cartes)
el.append(Spacer(1, 0.5*cm))
el.append(HRFlowable(width="100%", color=GRIS_C, thickness=1))
el.append(Spacer(1, 0.2*cm))
el.append(Paragraph("Données : football-data.co.uk (Premier League, E0). Stack : Python, pandas, scikit-learn, "
                    "matplotlib, ReportLab. Code et modèle exporté fournis avec ce rapport.", st_small))

# ----- PAGE 2 : METHODO -----
el.append(PageBreak())
el.append(Paragraph("1. La démarche", st_h))
el.append(Paragraph(
    "<b>Cible.</b> Une variable binaire : l’équipe à domicile gagne (1) ou non — nul ou défaite (0). "
    f"Sur la période, le domicile l’emporte dans <b>{res['taux_victoire_domicile']*100:.0f}%</b> des cas, "
    "ce qui fixe la barre à battre : un modèle qui prédirait systématiquement la classe majoritaire "
    f"atteindrait déjà <b>{res['accuracy_naif']*100:.0f}%</b> de bonnes réponses. Tout l’enjeu est de faire mieux que ce réflexe.", st_body))
el.append(Spacer(1, 0.2*cm))
el.append(Paragraph(
    "<b>Le piège évité : la fuite de données.</b> Il serait tentant d’utiliser les tirs, corners ou buts "
    "du match pour prédire son résultat. Mais ces statistiques ne sont connues qu’<i>après</i> le match : "
    "les utiliser donnerait un modèle brillant en apparence mais <b>inutilisable en conditions réelles</b>. "
    "J’ai donc construit des variables uniquement à partir de la <b>forme récente</b> de chaque équipe "
    f"(moyennes sur ses {res['fenetre']} derniers matchs : buts, tirs cadrés, points, etc.), "
    "toutes disponibles avant le coup d’envoi.", st_body))
el.append(Spacer(1, 0.2*cm))
el.append(Paragraph(
    "<b>Validation honnête.</b> Séparation chronologique train/test (on entraîne sur le passé, on teste "
    "sur les matchs les plus récents) et validation croisée à 5 plis. On ne triche jamais avec le futur.", st_body))

el.append(Paragraph("2. Résultats : quel modèle gagne ?", st_h))
rl, rf = res["resultats"]["Regression logistique"], res["resultats"]["Random Forest"]
data_tab = [
    ["Métrique", "Rég. logistique", "Random Forest"],
    ["Accuracy", f"{rl['accuracy']:.2f}", f"{rf['accuracy']:.2f}"],
    ["Précision", f"{rl['precision']:.2f}", f"{rf['precision']:.2f}"],
    ["Rappel (recall)", f"{rl['recall']:.2f}", f"{rf['recall']:.2f}"],
    ["F1-score", f"{rl['f1']:.2f}", f"{rf['f1']:.2f}"],
    ["AUC", f"{rl['auc']:.2f}", f"{rf['auc']:.2f}"],
]
tab = Table(data_tab, colWidths=[5*cm, 5.5*cm, 5.5*cm])
tab.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), BLEU), ("TEXTCOLOR",(0,0),(-1,0), colors.white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),10), ("ALIGN",(1,0),(-1,-1),"CENTER"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, GRIS_C]),
    ("GRID",(0,0),(-1,-1),0.5,colors.white), ("TOPPADDING",(0,0),(-1,-1),7),
    ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ("BACKGROUND",(2,5),(2,5), VERT), ("TEXTCOLOR",(2,5),(2,5), colors.white),
    ("FONTNAME",(2,5),(2,5),"Helvetica-Bold"),
]))
el.append(tab)
el.append(Spacer(1, 0.2*cm))
el.append(Paragraph(
    f"Le <b>{res['meilleur_modele']}</b> l’emporte de justesse (AUC {rf['auc']:.2f} contre {rl['auc']:.2f}). "
    f"Les deux modèles dépassent la référence naïve en accuracy ({rf['accuracy']*100:.0f}% vs "
    f"{res['accuracy_naif']*100:.0f}%) et surtout affichent une AUC nettement supérieure à 0,50 : "
    "ils captent un vrai signal. Restons lucides : <b>prédire le football reste difficile</b>, "
    "et c’est normal — l’aléa (un penalty, un carton rouge, un exploit individuel) est irréductible.", st_body))
el.append(Spacer(1, 0.3*cm))
el.append(img(os.path.join(FIG, "01_comparaison_modeles.png"), 13*cm))

# ----- PAGE 3 -----
el.append(PageBreak())
el.append(Paragraph("3. Lecture du meilleur modèle", st_h))
row = Table([[img(os.path.join(FIG,"02_matrice_confusion.png"), 8*cm),
              img(os.path.join(FIG,"03_courbe_roc.png"), 8*cm)]], colWidths=[8.5*cm,8.5*cm])
row.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
el.append(row)
el.append(Spacer(1, 0.2*cm))
el.append(Paragraph(
    "La matrice de confusion montre où le modèle se trompe ; la courbe ROC (au-dessus de la diagonale "
    "du hasard) confirme son pouvoir discriminant.", st_small))
el.append(Spacer(1, 0.3*cm))
el.append(Paragraph("4. Qu’est-ce qui compte le plus ?", st_h))
el.append(img(os.path.join(FIG,"04_importance_variables.png"), 13*cm))
el.append(Paragraph(
    "Sans surprise mais de façon rassurante, les variables de <b>différence de forme</b> entre les deux "
    "équipes (écart de points et de buts récents) dominent : le modèle a appris que l’écart de dynamique "
    "entre les adversaires est plus parlant que la forme d’une seule équipe prise isolément.", st_body))

# ----- PAGE 4 -----
el.append(PageBreak())
el.append(Paragraph("5. Bonus non supervisé : les styles d’équipes (KMeans)", st_h))
el.append(Paragraph(
    "En complément de la prédiction, j’ai appliqué un <b>KMeans</b> pour regrouper les équipes selon leur "
    "profil moyen (buts marqués/encaissés, tirs, points...). Sans jamais lui donner le classement, "
    f"l’algorithme retrouve <b>{res['kmeans_k']} familles</b> cohérentes, des cadors aux équipes "
    "luttant pour le maintien — une validation visuelle que les données portent bien une structure.", st_body))
el.append(Spacer(1, 0.3*cm))
el.append(img(os.path.join(FIG,"05_clusters_kmeans.png"), 11.5*cm))

el.append(Paragraph("6. Limites &amp; honnêteté", st_h))
for lim in [
    "L’échantillon couvre une seule ligue (Premier League) et 5 saisons : la généralisation à d’autres "
    "championnats reste à vérifier.",
    "Le modèle ignore des facteurs réels (blessures, fatigue, calendrier européen, météo, compositions) "
    "faute de données — d’où un plafond de performance attendu.",
    "Prédire le football est intrinsèquement bruité : une AUC autour de 0,65 est un résultat honnête, "
    "pas une boule de cristal. Ce projet illustre une démarche rigoureuse, pas un système de paris.",
]:
    el.append(Paragraph(f"• {lim}", st_body))
    el.append(Spacer(1, 0.1*cm))

el.append(Spacer(1, 0.3*cm))
concl = Table([[Paragraph(
    "<b>Ce que ce projet démontre.</b> Une chaîne complète et reproductible : collecte de données réelles, "
    "feature engineering sans fuite, comparaison de modèles supervisés, exploration non supervisée, "
    "sélection et export d’un modèle optimal prêt à prédire de nouveaux matchs — le tout avec un cadrage "
    "méthodologique transparent et des conclusions mesurées.",
    S("c", fontName="Helvetica", fontSize=10.5, textColor=colors.white, leading=16, alignment=TA_JUSTIFY))]],
    colWidths=[16*cm])
concl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLEU_F),("TOPPADDING",(0,0),(-1,-1),14),
                           ("BOTTOMPADDING",(0,0),(-1,-1),14),("LEFTPADDING",(0,0),(-1,-1),14),
                           ("RIGHTPADDING",(0,0),(-1,-1),14)]))
el.append(concl)

doc = SimpleDocTemplate(os.path.join(BASE, "Rapport_LinkedIn_Prediction_Foot.pdf"),
                        pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                        leftMargin=2*cm, rightMargin=2*cm,
                        title="Prediction resultat foot - Lucien Nzeutom")
doc.build(el, onFirstPage=couv, onLaterPages=lambda c,d: pied(c,d))
print("PDF genere avec accents.")
