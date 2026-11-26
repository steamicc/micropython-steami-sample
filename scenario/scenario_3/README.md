# 🛰️ STeaMi – Réseau BLE Maillé (3 Relais & 3 Périphériques)

Ce projet MicroPython met en œuvre un **réseau maillé Bluetooth Low Energy (BLE)** entre **6 nœuds** :  
3 **périphériques capteurs** (`STeaMi-P1`, `STeaMi-P2`, `STeaMi-P3`)  
et 3 **relais de communication** (`STeaMi-R1`, `STeaMi-R2`, `STeaMi-R3`).

Chaque périphérique lit une **distance** avec son capteur, **masque** la donnée par un XOR, puis l’envoie au **périphérique suivant** de la chaîne (P1 → P2 → P3 → P1).
Les relais forment un **maillage complet** : ils retransmettent les messages de manière distribuée, si bien qu’un message arrive même quand son destinataire est hors de portée de l’émetteur.
Chaque périphérique reçoit ainsi la distance du précédent et allume sa LED en fonction.

---

## 🔁 Topologie du réseau

<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">

  <!-- Périphériques -->
  <rect x="50" y="50" width="100" height="50" rx="10" ry="10" fill="#a2d5f2" stroke="#000"/>
  <text x="100" y="80" font-size="14" text-anchor="middle" fill="#000">P1</text>

  <rect x="250" y="50" width="100" height="50" rx="10" ry="10" fill="#f2a2a2" stroke="#000"/>
  <text x="300" y="80" font-size="14" text-anchor="middle" fill="#000">P2</text>

  <rect x="450" y="50" width="100" height="50" rx="10" ry="10" fill="#a2f2a2" stroke="#000"/>
  <text x="500" y="80" font-size="14" text-anchor="middle" fill="#000">P3</text>

  <!-- Relais -->
  <rect x="50" y="250" width="100" height="50" rx="10" ry="10" fill="#f2e2a2" stroke="#000"/>
  <text x="100" y="280" font-size="14" text-anchor="middle" fill="#000">R1</text>

  <rect x="250" y="175" width="100" height="50" rx="10" ry="10" fill="#f2c2f2" stroke="#000"/>
  <text x="300" y="205" font-size="14" text-anchor="middle" fill="#000">R2</text>

  <rect x="450" y="250" width="100" height="50" rx="10" ry="10" fill="#c2f2f2" stroke="#000"/>
  <text x="500" y="280" font-size="14" text-anchor="middle" fill="#000">R3</text>

  <!-- Flèches Périphérique -> Relais -->
  <line x1="100" y1="100" x2="100" y2="250" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="300" y1="100" x2="300" y2="175" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="500" y1="100" x2="500" y2="250" stroke="#000" marker-end="url(#arrow)"/>

  <!-- Flèches Relais -> Relais -->
  <line x1="150" y1="275" x2="250" y2="200" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="350" y1="200" x2="450" y2="275" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="250" y1="200" x2="150" y2="275" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="450" y1="275" x2="350" y2="200" stroke="#000" marker-end="url(#arrow)"/>

  <line x1="150" y1="280" x2="450" y2="280" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="450" y1="280" x2="150" y2="280" stroke="#000" marker-end="url(#arrow)"/>

  <!-- Flèches Relais -> Périphérique (retour) -->
  <line x1="100" y1="250" x2="100" y2="100" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="300" y1="175" x2="300" y2="100" stroke="#000" marker-end="url(#arrow)"/>
  <line x1="500" y1="250" x2="500" y2="100" stroke="#000" marker-end="url(#arrow)"/>

  <!-- Définition de flèche -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#000"/>
    </marker>
  </defs>
</svg>

Chaque relais communique avec :
- Son périphérique associé
- Les deux autres relais  
→ **Maillage complet** sans point central.

---

## 🔐 Format des messages

Une annonce BLE classique contient **31 octets au maximum**. Le message est donc codé en binaire dans le champ « manufacturer data », derrière l’identifiant de fabricant `0xFFFF` (réservé aux tests) :

| Champ | Type | Contenu |
| --- | --- | --- |
| `src` | `uint8` | Émetteur d’origine (indice dans `NODES` : 0 = P1 … 5 = R3) |
| `dst` | `uint8` | Destinataire |
| `seq` | `uint8` | Numéro de séquence de l’émetteur (0 à 255, puis recommence) |
| `hop` | `uint8` | Nombre de relais traversés |
| `value` | `int16` | Distance en mm |

Ces 6 octets sont masqués par un **XOR** avec une clé commune. Ce n’est pas un vrai chiffrement : il suffit de connaître la clé, ou d’essayer les 256 valeurs possibles.

```python
KEY = 0x5A
def xor_encrypt(data):
    return bytes(b ^ KEY for b in data)
```

Avec le nom du nœud (`STeaMi-P1`) et le champ Flags, l’annonce fait **24 octets**. Le format est défini dans `mesh.py`, commun aux périphériques et aux relais.

Le champ `hop` est incrémenté à chaque relais : au-delà de `MAX_HOPS` (3), le message n’est plus retransmis, ce qui évite les boucles infinies.

---

## 📡 Principe de fonctionnement

1. Périphérique
    * Lit la distance (`DISTANCE.read()`)
    * L’annonce pendant 500 ms, à destination du périphérique suivant (`P1` → `P2`), avec un nouveau numéro de séquence
    * Écoute ensuite les relais pendant 1 s pour recevoir les messages qui lui sont destinés
2. Relais
    * Écoute tous les nœuds pendant 800 ms
    * Ignore les messages déjà vus : il retient le dernier numéro de séquence de chaque émetteur
    * Retransmet chaque nouveau message sous son propre nom, avec `hop + 1`
3. Bouclage
    * Le message de `P1` est reçu par les relais à portée, par exemple `R1`
    * `R1` le retransmet ; `R2` et `R3` le retransmettent à leur tour s’ils ne l’ont pas déjà vu
    * `P2` reçoit le message d’un relais et réagit (LED allumée ou éteinte)

---

## 💡 Comportement des LEDs

Chaque périphérique allume sa LED quand la **distance reçue du périphérique précédent** est inférieure à 300 mm (`THRESHOLD_MM`), et l’éteint sinon :

| Périphérique | Réagit à    | LED       |
| ------------ | ----------- | --------- |
| `STeaMi-P1`  | `STeaMi-P3` | 🟢 Verte  |
| `STeaMi-P2`  | `STeaMi-P1` | 🔴 Rouge  |
| `STeaMi-P3`  | `STeaMi-P2` | 🔵 Bleue  |

Exemple :
* `P1` mesure `250 mm` → l’annonce pour `P2`
* `R1` (puis éventuellement `R2`, `R3`) retransmet
* `P2` reçoit `250` → allume sa LED rouge car `< 300`

## ⚙️ Fichiers principaux

`mesh.py` définit :
* La liste des nœuds (`NODES`) et le format binaire des messages
* `encode()` et `decode()`, avec le masquage XOR
* `is_new()`, qui écarte les messages déjà vus d’après leur numéro de séquence

`relay_base.py` gère :
* Le scan BLE
* Le décodage et la retransmission (`hop + 1`, limite `MAX_HOPS`)
* L’évitement des doublons
* L’affichage de l’état sur écran

`peripheral_base.py` gère :
* La lecture capteur
* L’émission BLE vers le périphérique suivant
* La réception de messages
* Le contrôle des LEDs
* L’affichage local

`pins.py` définit :

```python
DISTANCE = ...  # Objet avec .read()
LED_RED = ...
LED_GREEN = ...
LED_BLUE = ...
display = ...   # Objet OLED/I2C
```

---

## 🔧 Déploiement du scénario

| Nœud | Fichier à exécuter    | Fonction                    |
| ---- | --------------------- | --------------------------- |
| P1   | `scenario/scenario_3/peripheral_1/main.py` | Réagit à P3, LED verte      |
| P2   | `scenario/scenario_3/peripheral_2/main.py` | Réagit à P1, LED rouge      |
| P3   | `scenario/scenario_3/peripheral_3/main.py` | Réagit à P2, LED bleue      |
| R1   | `scenario/scenario_3/relay_1/main.py` | Relais du maillage          |
| R2   | `scenario/scenario_3/relay_2/main.py` | Relais du maillage          |
| R3   | `scenario/scenario_3/relay_3/main.py` | Relais du maillage          |

Chaque nœud importe `pins.py`, `mesh.py` et `peripheral_base.py` ou `relay_base.py`, placés dans `scenario/scenario_3/`. Monter ce dossier, puis lancer le `main.py` du nœud :

```bash
cd scenario/scenario_3
mpremote mount . exec "import sys; sys.path.insert(0, '/remote/peripheral_2'); import main"
```

---

## 📋 Exemple de log série

```
Relay STeaMi-R1 active
STeaMi-R1 relays 250 mm from STeaMi-P1 to STeaMi-P2 (hop 1)

Peripheral STeaMi-P2 active, sends to STeaMi-P3
STeaMi-P2 sent 812 mm to STeaMi-P3 (seq 43)
STeaMi-P2 received 250 mm from STeaMi-P1 via STeaMi-R1 (1 hops)
```

---

## 🧩 Avantages du système

✅ Maillage complet BLE : pas de point de défaillance unique
✅ Masquage XOR : les données ne sont pas lisibles en clair (sans être un vrai chiffrement)
✅ Propagation multi-sauts : communication indirecte fiable
✅ Architecture modulaire : facile à étendre à N relais / N périphériques
✅ Visualisation OLED : affichage local de l’état (V1a/V1b ; l’écran d’une V1c reste noir pour l’instant)

--- 

## 🚀 Extensions possibles

* 🧠 Implémenter un chiffrement AES pour sécuriser réellement le réseau
* 🕹️ Utiliser des services BLE GATT pour des échanges bidirectionnels fiables
* 🧩 Ajouter une topologie dynamique (auto-maillage)
* 🌐 Connecter un relais à Internet (IoT Gateway)

