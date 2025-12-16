moi=[{"nom": "Lucien", "age": 30, "ville": "Marseille"}, {"nom": "Marie", "age": 25, "ville": "Lyon"}, {"nom": "Paul", "age": 28, "ville": "Paris"}]


# Ce code parcourt une liste de dictionnaires représentant des personnes et affiche celles dont l'âge est supérieur à 27 ans.

def ajouter_personne(nom, age, ville):
    nouvelle_personne = {"nom": nom, "age": age, "ville": ville}
    moi.append(nouvelle_personne)
    return moi

ajouter_personne("Sophie", 32, "Nice")
print(moi)

# Cette fonction ajoute une nouvelle personne à la liste 'moi' et retourne la liste mise à jour.

def carre(x):
    return x * x

print(carre(5))
# Cette fonction calcule le carré d'un nombre donné et l'affiche pour l'entrée 5.

def filtrer_age(nom, age_limite):
    personnes_filtrees = []
    for personne in moi:
        if personne["age"] > age_limite:
            personnes_filtrees.append(personne)
    return personnes_filtrees
resultat = filtrer_age("age", 26)
print(resultat)