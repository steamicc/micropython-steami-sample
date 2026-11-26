# ⚡️ Consommation STeaMi

Ce dossier contient une série de programmes MicroPython permettant de **mesurer la consommation électrique** de la carte STeaMi dans différents scénarios d’utilisation (BLE, capteurs, périphériques).

Les scripts relèvent le courant consommé (en mA) avec la jauge de batterie BQ27441 (`BATTERY.current()`, couche `steami`) et affichent les résultats sur la console et l’écran OLED.

---

### 🛠 Mesure BLE Mode (Advertising Rapide/Lent)

Ce programme mesure la consommation en trois phases :

1. **Baseline (repos)** – sans activité BLE  
2. **Advertising rapide** – intervalle 100 ms  
3. **Advertising lent + lightsleep** – intervalle 1 s + mise en sommeil  

Résultats imprimés et affichés sur l’écran OLED.

---

### 🛠 Mesure BLE Scan + ADV

Ce programme mesure la consommation pendant :  

- **Scan actif** (recherche de périphériques BLE)  
- **Advertising** (envoi de trames publicitaires)  

Cela permet de comparer l’impact énergétique entre la recherche et l’annonce BLE.

---

### 🛠 Mesure BLE Talk (Connexion)

Ce programme joue le rôle de **central BLE** et de **peripheral BLE**.  
Il mesure la consommation moyenne lors de :  

1. **Repos (baseline)**  
2. **Scan actif** pour détecter un périphérique  
3. **Connexion et échanges de données** avec un périphérique (lecture de caractéristique, envoi du nom du client). 
4. **Advertising** pour trouver un point relais

---

### 🛠 Mesure Buzzer

Active le buzzer de la carte et mesure la consommation pendant un cycle d’activation/désactivation.  
Permet de connaître le surcoût énergétique lié au signal sonore.

---

### 🛠 Mesure Capteur Distance

Lit périodiquement la distance (capteur ToF / ultrason).  
Compare consommation **repos vs mesure active**.

---

### 🛠 Mesure LED

Active les LED embarquées (rouge/verte/bleue) individuellement ou ensemble, pour mesurer l’augmentation de consommation par couleur.

---

### 🛠 Mesure Écran OLED

Affiche du texte ou laisse l’écran éteint.  
Permet d’évaluer la différence de consommation liée à l’affichage.

---

### 🛠 Mesure Température & Humidité

Active la lecture du capteur environnement (température / humidité) et mesure la consommation associée.  
Compare consommation **repos vs acquisition périodique**.

---

## ✅ Utilisation

1. Copier le script correspondant sur la carte STeaMi.  
2. Démarrer le programme.  
3. Les moyennes de consommation sont :  
   - imprimées dans la console (`print`)  
   - affichées au centre de l’écran OLED.  

Chaque scénario calcule automatiquement une **moyenne en mA** sur une durée définie (ex. 5 secondes avec 1 mesure toutes les 0.5 s).

---

## 🔧 Exemple Résultat (console)

```python
[Baseline] Moyenne 3.20 mA
[Scan actif] Moyenne 8.45 mA
[Connexion] Moyenne 12.10 mA

===== Résultats consommation =====
Baseline: 3.20 mA
Scan: 8.45 mA
Connexion: 12.10 mA
=================================