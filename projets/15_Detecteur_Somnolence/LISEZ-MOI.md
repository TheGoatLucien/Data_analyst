# Détecteur de somnolence (webcam)

Un programme qui suit le visage en temps réel et alerte quand les yeux restent fermés
trop longtemps — l'idée étant de prévenir l'endormissement au volant. 100 % local,
rien n'est enregistré ni envoyé.

## Démo

Calibration sur les yeux ouverts au démarrage, puis : yeux fermés ~1,5 s → l'écran
passe au rouge « SOMNOLENCE » + un bip. Un bâillement est aussi signalé (en mode MediaPipe).

## Lancer

```bash
pip install -r requirements.txt
python detecteur_somnolence.py    # touche Q pour quitter
```

(Sous Windows, un double-clic sur `lancer.bat` fait l'installation + le lancement.)

## Comment ça marche

Le programme choisit automatiquement le meilleur moteur disponible :

- **OpenCV** (utilisé ici) : détection du visage et des yeux (cascades de Haar), puis
  mesure de la **netteté de la zone des yeux** via la variance du Laplacien. Un œil ouvert
  (iris, blanc, cils) est riche en détails ; un œil fermé est lisse → la valeur chute.
  Une **auto-calibration** au démarrage fixe le seuil sur le visage et la caméra de l'utilisateur.
- **MediaPipe** (si installé) : 468 points du visage et calcul de l'EAR (Eye Aspect Ratio),
  plus précis. Optionnel — le programme fonctionne sans.

Dans les deux cas, l'alerte se déclenche seulement si l'œil reste fermé au-delà d'un délai
(≈ 1,5 s), pour ne pas confondre un clignement avec un assoupissement.

## Choix techniques (et honnêteté)

J'ai d'abord visé MediaPipe (plus précis), mais son installation était cassée sur ma machine.
Plutôt que de rester bloqué, j'ai construit une version **100 % OpenCV** qui fonctionne sans
dépendance lourde. C'est moins fin que des points de repère faciaux, mais c'est robuste,
léger et entièrement local — un bon compromis face à une contrainte réelle d'environnement.

Limites : sensible à la lumière et à l'angle de la caméra ; les lunettes/reflets peuvent gêner.
C'est une démonstration pédagogique, pas un dispositif de sécurité homologué.

## Stack

Python · OpenCV · NumPy (MediaPipe en option).
