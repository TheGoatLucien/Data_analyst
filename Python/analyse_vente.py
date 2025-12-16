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


