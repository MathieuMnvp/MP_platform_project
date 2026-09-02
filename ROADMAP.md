# 🗺️ Roadmap : Plateforme de Couplage Multiphysique (OpenMC / OpenFOAM)

Cette feuille de route détaille l'état actuel et les futurs développements de la plateforme de couplage neutronique / thermo-hydraulique.

---

## 🟢 État actuel (Août 2026) : Couplage de base opérationnel
- [x] **Architecture :** Dossier `scenario` avec templates d'entrée et `config.json`.
- [x] **Physique :** Échange bidirectionnel (Puissance combustible $\leftrightarrow$ Température & Densité de l'eau).
- [x] **Solveur :** Boucle de couplage de type Gauss-Seidel implémentée.
- [x] **Géométrie :** Assemblage 3D fonctionnel (maillages OpenMC et OpenFOAM strictement identiques).

---

## 🟡 Phase 1 : Robustesse, Automatisation et Qualité (D'ici Nov/Déc 2026)
*Objectif : Rendre le code autonome, fiable et "pro".*

- [ ] **Critères de convergence :** Ajouter la vérification de la convergence dans la boucle Gauss-Seidel (sur la puissance, température, etc.) pour arrêter le calcul au bon moment.
- [ ] **Automatisation des I/O :** Automatiser à 100% la lecture des fichiers de sortie des deux codes (zéro modification manuelle, pilotage exclusif via le `config.json` du scénario).
- [O] **Reprise de calcul (Restart) :** Implémenter l'argument `restart=True` pour relancer un calcul interrompu sans manipulation humaine.
- [ ] **Francisation :** Traduire l'intégralité des commentaires du code en français.
- [ ] **Qualité du code ("Professionnalisation") :** Refactoriser le code (découpage en fonctions/classes propres, gestion des erreurs, standardisation du formatage).

---

## 🟠 Phase 2 : Changement d'échelle & Documentation (D'ici Fév/Mars 2027)
*Objectif : Préparer le code pour des géométries plus grandes et le rendre utilisable par d'autres.*

- [ ] **Mise à l'échelle spatiale :** Adapter le code pour gérer plusieurs assemblages en simultané.
- [ ] **Documentation :** Documenter proprement le code et ses fonctions (génération automatique d'une doc via Sphinx ou MkDocs).
- [ ] **Interface Physique (Hardware) :** Nettoyer et gérer proprement le script de contrôle du panneau LED affichant les résultats dans le bureau.

---

## 🔴 Phase 3 : Physique avancée & Cœur complet (D'ici Août 2027)
*Objectif : Pousser la physique à l'état de l'art et simuler un réacteur entier.*

- [ ] **Géométrie :** Adapter la plateforme pour un cœur entier.
- [ ] **Stabilité numérique (Sous-relaxation) :**
  - [ ] Ajouter une sous-relaxation constante.
  - [ ] Ajouter une sous-relaxation dynamique (méthode d'Aitken).
- [ ] **Nouveaux schémas de couplage :**
  - [ ] Jacobi.
  - [ ] JFNK (Jacobian-Free Newton-Krylov).
  - [ ] Accélération d'Anderson.
- [ ] **Dynamique / Transitoire :** Ajouter des scénarios non-statiques (cinétique spatiale, méthode Quasi-Statique...).
- [ ] **Multi-solveurs :** Intégrer **OpenMOC** (neutronique déterministe) comme alternative à OpenMC.

---

## 🟣 Phase 4 : Futur lointain (2028 et au-delà)
- [ ] **GUI :** Créer une interface graphique utilisateur (UI/UX) pour configurer les scénarios, lancer les calculs et visualiser les courbes de convergence en temps réel.
- [ ] **Mapping de maillage (Optionnel) :** *Note - Si le passage au cœur entier rend impossible d'avoir des maillages strictement identiques, il faudra développer ou intégrer un outil de projection/interpolation spatiale.*