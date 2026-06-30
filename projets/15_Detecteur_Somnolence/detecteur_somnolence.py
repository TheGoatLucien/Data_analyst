# -*- coding: utf-8 -*-
"""
==========================================================================================
 DETECTEUR DE SOMNOLENCE — vision par ordinateur en temps reel (webcam, 100% local)
==========================================================================================
But : prevenir l'endormissement au volant. La webcam suit le visage, mesure l'ouverture
des yeux, et declenche une alerte si les yeux restent fermes trop longtemps.

Deux modes, choisis automatiquement :
  - MEDIAPIPE (recommande, precis) : 468 points du visage, calcul de l'EAR (Eye Aspect
    Ratio), un ratio geometrique qui chute quand l'oeil se ferme.
  - OPENCV (secours, approximatif) : si MediaPipe n'est pas installe. On detecte visage et
    yeux (cascades Haar) et on mesure le CONTRASTE de la zone des yeux (un oeil ouvert a
    beaucoup plus de contraste qu'une paupiere fermee).

Auto-calibration au demarrage (yeux ouverts) : le seuil = 75% de la valeur "yeux ouverts".

Lancement :  python detecteur_somnolence.py      (touche Q pour quitter)
==========================================================================================
"""

import time
import math
import collections

import cv2
import numpy as np

try:
    # Import EXPLICITE du sous-module : les versions recentes de MediaPipe
    # n'exposent plus "mediapipe.solutions" via un simple "import mediapipe".
    import mediapipe.solutions.face_mesh as mp_face_mesh
    MEDIAPIPE_OK = True
    MEDIAPIPE_ERR = None
except Exception as exc:
    mp_face_mesh = None
    MEDIAPIPE_OK = False
    MEDIAPIPE_ERR = exc

SECONDES_ALERTE = 1.2
RATIO_SEUIL_FACTEUR = 0.75
FRAMES_CALIBRATION = 45
MAR_SEUIL = 0.6

OEIL_GAUCHE = [33, 160, 158, 133, 153, 144]
OEIL_DROIT = [362, 385, 387, 263, 373, 380]
BOUCHE = {"haut": 13, "bas": 14, "gauche": 78, "droite": 308}

VERT, ROUGE, JAUNE = (90, 220, 120), (60, 60, 235), (60, 200, 235)
BLANC, GRIS = (245, 245, 245), (160, 160, 160)


def distance(a, b):
    return math.dist(a, b)


def ratio_oeil(pts, idx):
    p = [pts[i] for i in idx]
    vert = distance(p[1], p[5]) + distance(p[2], p[4])
    horiz = 2.0 * distance(p[0], p[3])
    return vert / horiz if horiz else 0.0


def ratio_bouche(pts):
    larg = distance(pts[BOUCHE["gauche"]], pts[BOUCHE["droite"]])
    return distance(pts[BOUCHE["haut"]], pts[BOUCHE["bas"]]) / larg if larg else 0.0


class TrackerOpenCV:
    def __init__(self):
        base = cv2.data.haarcascades
        self.visage = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")
        self.yeux = cv2.CascadeClassifier(base + "haarcascade_eye.xml")
        if self.visage.empty() or self.yeux.empty():
            raise RuntimeError("Cascades Haar OpenCV introuvables.")

    def ouverture(self, frame):
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        visages = self.visage.detectMultiScale(gris, 1.2, 6, minSize=(120, 120))
        if len(visages) == 0:
            return None
        x, y, w, h = max(visages, key=lambda f: f[2] * f[3])
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
        haut = gris[y:y + int(h * 0.6), x:x + w]
        haut_col = frame[y:y + int(h * 0.6), x:x + w]
        yeux = self.yeux.detectMultiScale(haut, 1.1, 6, minSize=(25, 25))
        scores = []
        for (ex, ey, ew, eh) in sorted(yeux, key=lambda e: e[2] * e[3], reverse=True)[:2]:
            roi = haut[ey:ey + eh, ex:ex + ew]
            if roi.size:
                # variance du Laplacien = quantite de details/contours dans la zone.
                # Oeil ouvert (iris, blanc, cils) = beaucoup de details ; ferme = lisse.
                scores.append(float(cv2.Laplacian(roi, cv2.CV_64F).var()))
            cv2.rectangle(haut_col, (ex, ey), (ex + ew, ey + eh), (255, 255, 255), 1)
        if not scores:
            return 0.0
        return sum(scores) / len(scores)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Impossible d'ouvrir la webcam.")
        return

    mode = "mediapipe" if MEDIAPIPE_OK else "opencv"
    face_mesh = None
    tracker = None
    if mode == "mediapipe":
        try:
            face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True,
                min_detection_confidence=0.5, min_tracking_confidence=0.5)
        except Exception as exc:
            print("MediaPipe present mais erreur:", exc, "-> mode OpenCV.")
            mode = "opencv"
    if mode == "opencv":
        tracker = TrackerOpenCV()
        print("Mode OPENCV (secours). Pour la version precise, installe MediaPipe.")
        if MEDIAPIPE_ERR:
            print("  Raison MediaPipe indisponible :", MEDIAPIPE_ERR)
    else:
        print("Mode MEDIAPIPE (precis).")

    try:
        import winsound
        def bip():
            winsound.Beep(900, 250)
    except Exception:
        def bip():
            pass

    calib = []
    seuil = None
    ferme_depuis = None
    nb_alertes = 0
    dernier_bip = 0.0
    lisse = collections.deque(maxlen=5)
    print("Regarde la camera, yeux ouverts, pour la calibration. Q pour quitter.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        statut, couleur, mar = "Aucun visage", GRIS, None

        mesure = None
        if mode == "mediapipe":
            res = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if res.multi_face_landmarks:
                lm = res.multi_face_landmarks[0].landmark
                pts = [(int(p.x * w), int(p.y * h)) for p in lm]
                mesure = (ratio_oeil(pts, OEIL_GAUCHE) + ratio_oeil(pts, OEIL_DROIT)) / 2.0
                mar = ratio_bouche(pts)
                for i in OEIL_GAUCHE + OEIL_DROIT:
                    cv2.circle(frame, pts[i], 2, VERT, -1)
        else:
            mesure = tracker.ouverture(frame)

        val = None
        if mesure is not None:
            lisse.append(mesure)
            val = sum(lisse) / len(lisse)
            if len(calib) < FRAMES_CALIBRATION:
                calib.append(val)
                statut, couleur = "Calibration " + str(len(calib)) + "/" + str(FRAMES_CALIBRATION), JAUNE
                if len(calib) == FRAMES_CALIBRATION:
                    facteur = 0.75 if mode == "mediapipe" else 0.55
                    seuil = float(np.median(calib)) * facteur
            else:
                if val < seuil:
                    if ferme_depuis is None:
                        ferme_depuis = time.time()
                    if time.time() - ferme_depuis >= SECONDES_ALERTE:
                        statut, couleur = "! SOMNOLENCE !", ROUGE
                        if time.time() - dernier_bip > 1.0:
                            bip()
                            nb_alertes += 1
                            dernier_bip = time.time()
                    else:
                        statut, couleur = "Yeux fermes", JAUNE
                else:
                    ferme_depuis = None
                    if mar is not None and mar > MAR_SEUIL:
                        statut, couleur = "Baillement", JAUNE
                    else:
                        statut, couleur = "Eveille", VERT

        if statut == "! SOMNOLENCE !":
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), ROUGE, 14)
        cv2.rectangle(frame, (0, 0), (w, 46), (25, 25, 25), -1)
        cv2.putText(frame, "Etat : " + statut, (16, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.8, couleur, 2)
        cv2.putText(frame, "mode " + mode, (w - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GRIS, 1)
        if val is not None and seuil:
            cv2.putText(frame, "mesure %.2f / seuil %.2f" % (val, seuil), (16, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLANC, 1)
        cv2.putText(frame, "Alertes : " + str(nb_alertes), (16, h - 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLANC, 1)
        cv2.putText(frame, "Q : quitter", (w - 130, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GRIS, 1)

        cv2.imshow("Detecteur de somnolence - Lucien Nzeutom", frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
            break

    cap.release()
    cv2.destroyAllWindows()
    if face_mesh is not None:
        face_mesh.close()


if __name__ == "__main__":
    main()
