;; ==========================================================
;; УРОВЕНЬ 2. ПСИХИАТРИЯ (salience 50)
;; ==========================================================

;; --- Паника ---
(defrule syn-panic-attack
   (declare (salience 50))
   (symptom (name panic-attack))
   => (bump-syndrome panic-disorder 0.6))

(defrule syn-panic-palpit
   (declare (salience 50))
   (symptom (name palpitations))
   => (bump-syndrome panic-disorder 0.2))

(defrule syn-panic-sweat
   (declare (salience 50))
   (symptom (name sweating))
   => (bump-syndrome panic-disorder 0.15))

;; --- Депрессия ---
(defrule syn-depr-mood
   (declare (salience 50))
   (symptom (name low-mood))
   => (bump-syndrome depression 0.45))

(defrule syn-depr-anhedonia
   (declare (salience 50))
   (symptom (name anhedonia))
   => (bump-syndrome depression 0.45))

(defrule syn-depr-insomnia
   (declare (salience 50))
   (symptom (name insomnia))
   => (bump-syndrome depression 0.3))

(defrule syn-depr-fatigue
   (declare (salience 50))
   (symptom (name fatigue))
   => (bump-syndrome depression 0.15))