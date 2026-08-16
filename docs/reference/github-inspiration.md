# gestureOS — Deep-dive technique

**Repo local :** `/home/anthony/Documents/perso/projects/chrysa/gestureOS`
**Remote :** `github.com/chrysa/gestureOS` · **Licence projet :** MIT © chrysa
**Date :** 2026-08-15

## Ce que fait le projet (1 phrase)

gestureOS transforme n'importe quelle webcam en périphérique d'entrée mains-libres —
déplacement/clic/scroll/drag du curseur et contrôle média par gestes de la main + regard,
sur 1 à 4 écrans, via un pipeline perception→action à faible latence (budget p95 < 50 ms).

## État réel du repo (constaté)

- **Pré-alpha / bootstrap.** Seul le socle `core/` existe (`events.py`, `protocols.py`,
  `types.py`, `bus.py` — pub/sub typé + fast-path latence) plus le harnais de bench
  (`gestureos/perf.py`) et une CLI stub (`gestureos/cli.py`) qui n'imprime que sa version.
- Le pipeline webcam (capture → MediaPipe → geste/gaze → résolution → OS control) **n'est
  pas implémenté** : cf. `plans/gestureos-construction.md` (plan multi-PR).
- Deps clés déjà déclarées : `mediapipe>=0.10.35`, `opencv-python-headless`, `numpy>=2`,
  `pydantic`, `click`, `rich`, `screeninfo` ; backend Windows optionnel
  (`pyautogui`/`pywin32`/`pygetwindow`) sous markers de plateforme. Python 3.14, mypy strict.
- Jumeau : `voiceOS` (twin voix), partage le même `core/` (DECISIONS.md D-0002).

Le projet est un produit d'application (pas une lib interne) : il **a** des équivalents
OSS directs et matures. On garde 5 références, chacune éclairant une couche distincte du
pipeline (perception main, perception regard, mapping geste→souris, contrôle OS
cross-platform, moteur ML). C'est le bon nombre ici — au-delà ce ne serait que des clones
de virtual-mouse étudiants sans valeur additionnelle.

---

## google-ai-edge/mediapipe

- **Owner/repo :** google-ai-edge/mediapipe
- **Stars :** ~36.6k · **Activité :** très active (5 586 commits, PRs/issues ouvertes en continu)
- **Langage :** C++/Python · **Licence :** **Apache-2.0 (permissive — copiable/liable)**
- **Module du pattern :** MediaPipe Tasks — `HandLandmarker` et `GestureRecognizer`
  (Python `mediapipe.tasks.python.vision`).
- **Mécanisme réel :** modèles pré-entraînés (`.task` bundles). `HandLandmarker` renvoie
  21 landmarks 3D/main + handedness ; `GestureRecognizer` ajoute une tête de classification
  (7 gestes canned : Open_Palm, Closed_Fist, Pointing_Up, Thumb_Up/Down, Victory, ILoveYou).
  Mode `LIVE_STREAM` avec callback asynchrone + timestamp — exactement le modèle qu'attend
  le fast-path de `core/bus.py`.
- **Snippet portable :**
  ```python
  from mediapipe.tasks.python import vision, BaseOptions

  def _on_result(result, image, ts_ms: int) -> None:
      if result.hand_landmarks:
          idx_tip = result.hand_landmarks[0][8]   # index fingertip (x,y normalisés)
          bus.publish(LandmarkEvent(x=idx_tip.x, y=idx_tip.y, t_ms=ts_ms))

  opts = vision.HandLandmarkerOptions(
      base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
      running_mode=vision.RunningMode.LIVE_STREAM,
      num_hands=1,
      result_callback=_on_result,
  )
  landmarker = vision.HandLandmarker.create_from_options(opts)
  landmarker.detect_async(mp_image, timestamp_ms)   # non-bloquant
  ```
- **Intégration gestureOS :** implémenter le stage `inference` derrière un
  `Protocol` de `core/protocols.py` ; le callback `detect_async` publie un
  `LandmarkEvent` sur le bus → alimente le stage `landmark→gesture`. Utiliser
  `RunningMode.LIVE_STREAM` (pas `VIDEO`) pour ne pas bloquer la boucle capture.
- **Gotchas :** le callback tourne sur un thread interne MediaPipe → toute mutation d'état
  doit passer par le bus thread-safe, pas par des attributs partagés. Les `.task` (~7-8 Mo)
  ne doivent pas être committés : les fetch au build/install. `opencv-python-headless`
  (déjà choisi) évite le conflit de libGL en CI. Latence inference CPU ~15-25 ms : c'est le
  plus gros poste du budget 50 ms — prévoir un flag GPU/delegate.

## antoinelame/GazeTracking

- **Owner/repo :** antoinelame/GazeTracking
- **Stars :** ~2.6k · **Activité :** modérée (34 commits, projet mûr/stable)
- **Langage :** Python · **Licence :** **MIT (permissive — copiable)**
- **Module du pattern :** classe `GazeTracking` — `horizontal_ratio()`, `vertical_ratio()`,
  `is_left/right/center()`, `pupil_left_coords()`.
- **Mécanisme réel :** détecte les yeux (dlib landmarks à l'origine), isole la région
  oculaire, seuille l'iris pour trouver le centre de la pupille, puis calcule un **ratio**
  position-pupille / largeur-œil (0.0 = extrême droite → 1.0 = extrême gauche). C'est ce
  ratio normalisé — pas une position écran absolue — qui est robuste et directement
  utilisable pour le *screen focus* de gestureOS.
- **Snippet portable :**
  ```python
  # remplacer dlib par MediaPipe FaceMesh iris (landmarks 468-477) pour rester sur une
  # seule stack de perception, mais garder la logique de ratio :
  def horizontal_ratio(iris_x: float, eye_left_x: float, eye_right_x: float) -> float:
      return (iris_x - eye_left_x) / (eye_right_x - eye_left_x)  # 0..1

  def focused_screen(ratio_h: float, n_screens: int) -> int:
      return min(int(ratio_h * n_screens), n_screens - 1)
  ```
- **Intégration gestureOS :** alimente la feature *gaze-based screen focus* (choisir lequel
  des 1-4 écrans reçoit l'input). Ne PAS l'utiliser pour le pointage fin (jitter trop élevé
  en webcam) — le geste de la main fait le pointage, le regard fait juste la sélection d'écran.
- **Gotchas :** dépend historiquement de **dlib** (compilation lourde, modèle
  shape_predictor à part) — préférer réimplémenter le *ratio* sur MediaPipe FaceMesh iris
  (déjà dans la stack) plutôt qu'ajouter dlib. Très sensible à l'éclairage ; prévoir une
  calibration + hystérésis pour éviter le flip d'écran permanent à la frontière.

## Viral-Doshi/Gesture-Controlled-Virtual-Mouse

- **Owner/repo :** Viral-Doshi/Gesture-Controlled-Virtual-Mouse
- **Stars :** ~845 · **Activité :** peu active (165 commits, projet figé)
- **Langage :** Python · **Licence :** **GPL-3.0 → COPYLEFT — RÉIMPLÉMENTER, ne pas copier le code**
- **Module du pattern :** `src/Gesture_Controller.py`.
- **Mécanisme réel (à ré-exprimer soi-même) :** curseur assigné au **midpoint index+majeur**
  (plus stable qu'un seul doigt) ; gestes de pinch **dynamiques et proportionnels** — la
  vitesse de scroll/volume/luminosité est proportionnelle à la distance parcourue par le
  pinch depuis son point de départ ; vitesse curseur proportionnelle à la vitesse de la main
  (accélération type pointer-ballistics). Ce sont des *idées de design*, pas du code — donc
  librement réimplémentables malgré la GPL.
- **Snippet portable (réécrit from scratch, pas issu du repo) :**
  ```python
  def cursor_anchor(idx_tip, mid_tip):           # midpoint = moins de jitter
      return ((idx_tip.x + mid_tip.x) / 2, (idx_tip.y + mid_tip.y) / 2)

  def pinch_scroll_speed(dist_now: float, dist_start: float, gain: float = 40.0) -> float:
      return (dist_now - dist_start) * gain      # proportionnel, signé
  ```
- **Intégration gestureOS :** informe la table de résolution du stage
  `landmark→gesture`/`resolve` (pinch→click, distance-proportionnelle→scroll). À coder dans
  vos propres modules typés sous `gestureos/`.
- **Gotchas :** **GPL-3.0** — interdit de vendorer/adapter le code source dans un projet MIT.
  N'en reprendre que les concepts. Le repo mélange aussi un assistant vocal (`Proton.py`) :
  hors scope (voiceOS gère ça).

## moses-palmer/pynput

- **Owner/repo :** moses-palmer/pynput
- **Stars :** ~2.2k · **Activité :** active/maintenue
- **Langage :** Python · **Licence :** **LGPL-3.0 → copyleft FAIBLE : utilisable comme
  dépendance importée sans contaminer, mais NE PAS vendorer/modifier le source**
- **Module du pattern :** `pynput.mouse.Controller` / `pynput.keyboard.Controller` +
  backends par OS (`_win32`, `_darwin`, `_xorg`) sélectionnés à l'import.
- **Mécanisme réel :** façade unique ; chaque OS a un backend concret chargé dynamiquement.
  `Controller().position = (x, y)`, `.click(Button.left)`, `.scroll(dx, dy)`. Exactement le
  pattern « un Protocol, N backends + no-op headless » que gestureOS décrit dans README/architecture.
- **Snippet portable :**
  ```python
  # gestureOS définit son propre Protocol ; pynput est une impl possible du backend
  from pynput.mouse import Controller, Button

  class PynputMouseBackend:                       # satisfait core.protocols.OSControl
      def __init__(self) -> None: self._m = Controller()
      def move_to(self, x: int, y: int) -> None: self._m.position = (x, y)
      def click(self) -> None: self._m.click(Button.left, 1)
      def scroll(self, dy: int) -> None: self._m.scroll(0, dy)
  ```
- **Intégration gestureOS :** candidat sérieux pour **unifier** le backend OS-control
  Linux+Windows+macOS derrière un seul Protocol, au lieu de câbler ydotool/xdotool/wmctrl
  (Linux) + pywin32/pyautogui (Windows) séparément. Garder le backend no-op pour la CI headless.
- **Gotchas :** **LGPL** → l'importer via pip (dépendance dynamique) est OK pour un projet
  MIT ; interdit de copier/forker son code dans le repo. Sous Wayland, pynput/Xorg est
  limité — c'est précisément pourquoi le README cite `ydotool` (uinput) : garder un backend
  ydotool en fallback Wayland. macOS exige les permissions Accessibility.

## cvzone/cvzone

- **Owner/repo :** cvzone/cvzone
- **Stars :** ~1.3k · **Activité :** maintenue · **Langage :** Python
- **Licence :** **MIT (permissive — copiable)**
- **Module du pattern :** `cvzone.HandTrackingModule.HandDetector` — `fingersUp()`,
  `findDistance()`.
- **Mécanisme réel :** wrapper mince au-dessus de MediaPipe Hands. `fingersUp()` renvoie une
  liste `[0/1]*5` (doigt levé/baissé) via comparaison des landmarks tip vs pip ; `findDistance()`
  donne la distance pixel entre deux landmarks (base du détecteur de pinch). C'est l'algèbre
  exacte dont a besoin le stage `landmark→gesture`.
- **Snippet portable (logique fingersUp réimplémentable trivialement) :**
  ```python
  def fingers_up(lm) -> list[int]:               # lm = 21 landmarks
      up = [1 if lm[t].y < lm[t - 2].y else 0 for t in (8, 12, 16, 20)]  # 4 doigts
      up.insert(0, 1 if lm[4].x < lm[3].x else 0)                         # pouce (main droite)
      return up

  def is_pinch(lm, thresh: float = 0.05) -> bool:
      return math.hypot(lm[4].x - lm[8].x, lm[4].y - lm[8].y) < thresh
  ```
- **Intégration gestureOS :** deux options — (a) dépendance directe `cvzone` (MIT, sans
  risque) pour prototyper vite le stage geste ; (b) réimplémenter `fingers_up`/`is_pinch`
  (10 lignes) pour garder zéro dépendance transitive et un typage strict mypy. Recommandé :
  (b) en prod (cvzone tire tout OpenCV non-headless), (a) pour un spike.
- **Gotchas :** cvzone importe `opencv-python` (avec GUI) — conflit possible avec votre
  `opencv-python-headless` en CI. Son `fingersUp` suppose une orientation main verticale ;
  fragile si la main est inclinée → normaliser sur l'axe poignet→majeur avant seuillage.

---

## Synthèse licences

| Source | Licence | Verdict |
| --- | --- | --- |
| google-ai-edge/mediapipe | Apache-2.0 | ✅ permissive — liable/copiable |
| antoinelame/GazeTracking | MIT | ✅ permissive — copiable |
| cvzone/cvzone | MIT | ✅ permissive — copiable |
| moses-palmer/pynput | LGPL-3.0 | ⚠️ copyleft faible — importer OK, NE PAS vendorer |
| Viral-Doshi/Gesture-Controlled-Virtual-Mouse | GPL-3.0 | ⛔ copyleft fort — RÉIMPLÉMENTER les idées uniquement |

**Recommandation stack :** MediaPipe Tasks (perception main+iris, un seul moteur ML) →
réimplémenter fingers_up/pinch/gaze-ratio en interne (typé, testable, sans dette de licence)
→ backend OS-control derrière un Protocol, pynput importé comme dép + fallback ydotool
(Wayland/uinput) + no-op headless.
