;; ==========================================================
;; УРОВЕНЬ 2. КАРДИОЛОГИЯ (salience 50)
;; ==========================================================

(defrule syn-cardiac-pain
   (declare (salience 50))
   (symptom (name chest-pain))
   => (bump-syndrome cardiac 0.3))

(defrule syn-cardiac-radiation
   (declare (salience 50))
   (symptom (name chest-radiation))
   => (bump-syndrome cardiac 0.45))

(defrule syn-cardiac-dyspnea
   (declare (salience 50))
   (symptom (name dyspnea))
   => (bump-syndrome cardiac 0.2))

(defrule syn-cardiac-sweating
   (declare (salience 50))
   (symptom (name sweating))
   => (bump-syndrome cardiac 0.2))

(defrule syn-cardiac-nausea
   (declare (salience 50))
   (symptom (name nausea))
   => (bump-syndrome cardiac 0.15))

(defrule syn-cardiac-palpitations
   (declare (salience 50))
   (symptom (name palpitations))
   => (bump-syndrome cardiac 0.25))