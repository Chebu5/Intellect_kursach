;; ==========================================================
;; УРОВЕНЬ 2. ГАСТРОЭНТЕРОЛОГИЯ (salience 50)
;; ==========================================================

(defrule syn-gerd-heartburn
   (declare (salience 50))
   (symptom (name heartburn))
   => (bump-syndrome gerd 0.45))

(defrule syn-gerd-sour
   (declare (salience 50))
   (symptom (name sour-taste))
   => (bump-syndrome gerd 0.4))

(defrule syn-gerd-meals
   (declare (salience 50))
   (symptom (name worse-after-meals))
   => (bump-syndrome gerd 0.3))

(defrule syn-gerd-chest-pain
   (declare (salience 50))
   (symptom (name chest-pain))
   => (bump-syndrome gerd 0.15))