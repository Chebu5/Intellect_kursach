;; ==========================================================
;; УРОВЕНЬ 2. ПУЛЬМОНОЛОГИЯ (salience 50)
;; ==========================================================

(defrule syn-pulmo-pleuritic
   (declare (salience 50))
   (symptom (name worse-on-inspiration))
   => (bump-syndrome pulmonary 0.5))

(defrule syn-pulmo-cough
   (declare (salience 50))
   (symptom (name cough))
   => (bump-syndrome pulmonary 0.25))

(defrule syn-pulmo-fever
   (declare (salience 50))
   (symptom (name fever))
   => (bump-syndrome pulmonary 0.2))

(defrule syn-pulmo-wheezing
   (declare (salience 50))
   (symptom (name wheezing))
   => (bump-syndrome pulmonary 0.4))

(defrule syn-pulmo-dyspnea
   (declare (salience 50))
   (symptom (name dyspnea))
   => (bump-syndrome pulmonary 0.25))