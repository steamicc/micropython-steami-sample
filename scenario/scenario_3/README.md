# 🛰️ STeaMi – Réseau BLE Maillé Chiffré (3 Relais & 3 Périphériques) (Non-fonctionnelle)

Ce projet MicroPython met en œuvre un **réseau maillé Bluetooth Low Energy (BLE)** entre **6 nœuds** :  
3 **périphériques capteurs** (`STeaMi-P1`, `STeaMi-P2`, `STeaMi-P3`)  
et 3 **relais de communication** (`STeaMi-R1`, `STeaMi-R2`, `STeaMi-R3`).

Chaque périphérique lit une **distance** à partir de son capteur, **chiffre** la donnée, puis l’envoie à son relais associé.  
Les relais forment ensuite un **maillage complet** — ils s’échangent et retransmettent les messages de manière distribuée.  
Chaque périphérique suivant dans la chaîne reçoit et **analyse** la donnée du précédent.

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

## 🔐 Chiffrement

Toutes les communications BLE entre nœuds sont **chiffrées par un XOR simple** avec une clé commune :

```python
KEY = 0x5A
def xor_encrypt(data):
    return bytes([b ^ KEY for b in data])
```

Chaque message BLE contient une trame JSON chiffrée dans le champ "manufacturer data" :

```json
{
  "src": "STeaMi-P1",
  "dst": "STeaMi-R1",
  "payload": 254,
  "hop": 0
}
```

Le champ `hop` est incrémenté à chaque relais pour éviter les boucles infinies.

---

## 📡 Principe de fonctionnement

1. Périphérique
    * Lit la distance (`DISTANCE.read()`)
    * Chiffre la valeur avec `xor_encrypt`
    * L’envoie via BLE à son relais associé (ex. `P1` → `R1`)
    * Scanne ensuite le réseau pour recevoir les messages lui étant destinés
2. Relais
    * Scanne en continu le réseau BLE
    * Déchiffre les messages reçus
    * Évite les doublons avec un cache `seen_msgs`
    * Retransmet les messages à tous les autres relais et périphériques
3. Bouclage
    * Le message de `P1` est reçu par `R1`
    * `R1` diffuse à `R2` et `R3`
    * `R2` le rediffuse, jusqu’à atteindre `P2`
    * `P2` déchiffre et réagit (LED ON/OFF)

---

## 💡 Comportement des LEDs

| Périphérique | LED active si distance < 300 | LED active si distance ≥ 300 |
| ------------ | ---------------------------- | ---------------------------- |
| `STeaMi-P1`  | 🟢 **Verte**                 | 🔴 **Rouge**                 |
| `STeaMi-P2`  | 🔴 **Rouge**                 | 🔵 **Bleue**                 |
| `STeaMi-P3`  | 🔵 **Bleue**                 | 🟢 **Verte**                 |

Chaque périphérique s’allume selon la **distance reçue du périphérique précédent.**

Exemple :
* `P1` mesure `250 cm` → envoie à `R1`
* `R1` → `R2` → `R3` → `P2`
* `P2` reçoit `250` → allume sa LED rouge car `< 300`

## ⚙️ Fichiers principaux

`relay_base.py` gère :
* Le scan BLE
* Le déchiffrement et la redistribution
* L’évitement de doublons (seen_msgs)
* L’affichage de l’état sur écran

`peripheral_base.py` gère :
* La lecture capteur
* L’émission BLE chiffrée
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
| P1   | `scenario/scenario_3/peripheral_1/main.py` | Capteur distance, LED verte |
| P2   | `scenario/scenario_3/peripheral_2/main.py` | Réagit à P1, LED rouge      |
| P3   | `scenario/scenario_3/peripheral_3/main.py` | Réagit à P2, LED bleue      |
| R1   | `scenario/scenario_3/relay_1/main.py` | Relais de P1                |
| R2   | `scenario/scenario_3/relay_2/main.py` | Relais de P2                |
| R3   | `scenario/scenario_3/relay_3/main.py` | Relais de P3                |

---

## 📋 Exemple de log série

```
Device name: STeaMi-R1
Relay STeaMi-R1 active
Received: {"src":"STeaMi-P1","dst":"STeaMi-R1","payload":250,"hop":0}
Relaying message to mesh...
Advertisement done.

Device name: STeaMi-P2
Peripheral STeaMi-P2 active
Received distance 250 from R1
LED_RED ON
```

---

## 🧩 Avantages du système

✅ Maillage complet BLE : pas de point de défaillance unique
✅ Chiffrement basique intégré : confidentialité des échanges
✅ Propagation multi-sauts : communication indirecte fiable
✅ Architecture modulaire : facile à étendre à N relais / N périphériques
✅ Visualisation OLED : affichage local clair des distances

--- 

## 🚀 Extensions possibles

* 🔄 Ajouter une gestion TTL pour les paquets (limiter les boucles)
* 🧠 Implémenter un chiffrement AES pour sécuriser réellement le réseau
* 🕹️ Utiliser des services BLE GATT pour des échanges bidirectionnels fiables
* 🧩 Ajouter une topologie dynamique (auto-maillage)
* 🌐 Connecter un relais à Internet (IoT Gateway)

