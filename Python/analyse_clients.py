import pandas as pd
import matplotlib.pyplot as plt
df= pd.read_csv("clients_clean.csv")

print(df)

print(df.head())
print(df.info())
print(df.describe())

clients_par_ville = df["ville"].value_counts()
print(clients_par_ville)

clients_par_ville.plot(kind="bar")
plt.title("Nombre de clients par ville")
plt.xlabel("Ville")
plt.ylabel("Nombre de clients")
plt.show()


def categorie_age(age):
    if age < 18:
        return "Mineur"
    elif 18 <= age < 65:
        return "Adulte"
    else:
        return "Senior"
df["categorie_age"]= df["age"].apply(categorie_age)
df["categorie_age"].value_counts().plot(kind= "pie", autopct="%1.1f%%")
plt.title("Répartition des clients par catégorie d'âge")
plt.ylabel("")
plt.show()

df["age"].plot(kind="hist", bins=20) # Histogramme des âges des clients
plt.title("Diistribution des ages des clients")
plt.xlabel("Age")
plt.ylabel("Nombre de clients")
plt.show()

#line chhart des clients par ville d'inscription

clients_par_annee = df["ville"].value_counts().sort_index()
clients_par_annee.plot(kind="line", marker="o")
plt.title("Nombre de clients par ville d'inscription")
plt.xlabel("Ville")
plt.ylabel("Nombre de clients")
plt.show()