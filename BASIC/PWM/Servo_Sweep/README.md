# Test de Servo Moteur - Balayage (Sweep)

Test basique pour valider le fonctionnement d'un servo moteur avec PWM sur STM32.

## Description

Ce programme :
1. Détecte automatiquement quel Timer et Canal PWM fonctionnent pour une pin donnée
2. Effectue un balayage du servo de -90° à +90° puis retour
3. Affiche les informations de debug pour le développement

## Utilisation

### Câblage

Connectez votre servo :
- **Signal** : Sur la pin configurée (par défaut P11)
- **VCC** : Sur le +5V
- **GND** : Sur la masse

### Configuration

Dans le fichier `main.py`, modifiez les constantes selon votre câblage :

```python
DEFAULT_PIN = "P11"     # Pin où est connecté le servo
```

### Exécution

Depuis le dossier du projet :

```bash
cd /home/nedjar/sandbox/micropython-steami-sample
mpremote mount . run BASIC/PWM/Servo_Sweep/main.py
```

Ou depuis le dossier `BASIC/PWM/Servo_Sweep` :

```bash
cd BASIC/PWM/Servo_Sweep
mpremote mount /home/nedjar/sandbox/micropython-steami-sample run main.py
```

## Sortie attendue

```
============================================================
Test de Servo Moteur - Balayage (Sweep)
============================================================

Configuration:
  Pin: P11

============================================================
MÉTHODE 1: Détection automatique
============================================================

============================================================
Détection automatique pour la pin P11
============================================================
Essai: Timer 1 Canal 1... ✓ SUCCÈS!

✓ Configuration trouvée: Timer 1, Canal 1

Lancement du test de balayage...

==================================================
Test servo sur P11 avec Timer 1 Canal 1
==================================================
✓ Pin P11 créée
✓ Timer 1 initialisé à 50Hz
✓ Canal 1 PWM créé

Test de balayage du servo:
Le servo va bouger de -90° à +90° puis retour

Balayage vers la droite (-90° -> +90°)...
  Angle:  -90° (duty: 5.0%)
  Angle:  -80° (duty: 5.3%)
  ...
  Angle:   90° (duty: 10.0%)

Balayage vers la gauche (+90° -> -90°)...
  Angle:   90° (duty: 10.0%)
  ...
  Angle:  -90° (duty: 5.0%)

Retour au centre (0°)...

✓ Test réussi!
  La pin P11 fonctionne avec Timer 1 Canal 1
```

## Pins PWM disponibles sur STM32G431KB (STEAMI)

Selon la configuration STM32, voici les pins qui supportent le PWM :

| Pin Arduino | Pin STM32 | Timer     | Commentaire |
|-------------|-----------|-----------|-------------|
| P0          | PA_0      | TIM2_CH1  | ✓ Recommandé |
| P1          | PA_1      | TIM2_CH2  | ✓ Recommandé |
| P2          | PA_2      | TIM2_CH3  | ✓ Recommandé |
| P11         | PA_8      | TIM1_CH1  | ✓ Recommandé |
| -           | PA_9      | TIM1_CH2  | Si accessible |
| -           | PA_10     | TIM1_CH3  | Si accessible |
| P14         | PB_14     | TIM1_CH2N | ✗ Canal inversé, problématique |

## Dépannage

### Le servo ne bouge pas

1. Vérifiez l'alimentation (le servo a besoin de 5V avec assez de courant)
2. Vérifiez le câblage (signal, VCC, GND)
3. Essayez une autre pin de la liste ci-dessus
4. Vérifiez que le servo n'est pas bloqué mécaniquement

### Erreur "Pin doesn't support PWM"

La pin choisie ne supporte pas le PWM. Modifiez `DEFAULT_PIN` pour utiliser une des pins recommandées ci-dessus.

### Le servo tremble ou vibre

C'est souvent dû à :
- Une alimentation insuffisante
- Des interférences électriques
- Un servo de mauvaise qualité

## Pour aller plus loin

Une fois que vous avez identifié la configuration Timer/Canal qui fonctionne, vous pouvez :

1. **Mettre à jour la bibliothèque du robot** avec les bonnes valeurs
2. **Créer des mouvements personnalisés** en modifiant les angles
3. **Contrôler plusieurs servos** en utilisant différentes pins PWM

## Fonctions utiles

### `test_servo_on_pin(pin_name, timer_id, channel_id)`

Test un servo avec une configuration spécifique.

### `auto_detect_servo_pin(pin_name)`

Détecte automatiquement la configuration PWM pour une pin.

### `angle_to_duty(angle)`

Convertit un angle (-90° à 90°) en pourcentage de duty cycle.
