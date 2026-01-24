import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

df= pd.read_csv("ventes.csv")
df.head()
df.info()
df.describe()

#ventes par produit
df_produit= df.groupby("produit")["vente"].sum()
df_produit.plot(kind="bar")
plt.title("Nombre de ventes par produit")
plt.xlabel("Produit")
plt.ylabel("Nombre de ventes")
plt.show()

#ventes par mois
# Définir l'ordre correct des mois
mois_ordre = ["janvier", "février", "mars", "avril", "mai", "juin", 
              "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

# Convertir la colonne "mois" en catégorie ordonnée
df["mois"] = pd.Categorical(df["mois"], categories=mois_ordre, ordered=True)

ventes_par_mois= df.groupby("mois")["vente"].sum()  
ventes_par_mois.plot(kind="line", marker="o")
plt.title("Nombre de ventes par mois")
plt.xlabel("Mois")
plt.ylabel("Nombre de ventes")
plt.show()

#ventes par categories
df_categorie= df.groupby("categorie")["vente"].sum()
df_categorie.plot(kind="pie", autopct="%1.1f%%")
plt.title("Répartition des ventes par catégorie")
plt.ylabel("")  
plt.show()


#KPI 1 — Total des ventes
total_ventes= df["vente"].sum()
print(f"Total des ventes : {total_ventes}")

#KPI 2 — Part de chaque produit (%)
part_produit=(df_produit/ total_ventes)*100
print("Part de chaque produit (%):", part_produit)

#KPI 3 — Croissance mensuelle (%)
croissance_mensuelle= ventes_par_mois.pct_change()*100
print("Croissance mensuelle (%):", croissance_mensuelle)

#KPI 4 — Produit le plus vendu
produit_le_plus_vendu= df_produit.idxmax()
print(f"Produit le plus vendu : {produit_le_plus_vendu}")

