;; ==========================================================
;; УРОВЕНЬ 2. ЭНДОКРИНОЛОГИЯ (salience 50)
;; ==========================================================

;; --- Диабет ---
(defrule syn-diab-polyuria
   (declare (salience 50))
   (symptom (name polyuria))
   => (bump-syndrome diabetes 0.35))

(defrule syn-diab-polydipsia
   (declare (salience 50))
   (symptom (name polydipsia))
   => (bump-syndrome diabetes 0.35))

(defrule syn-diab-weightloss
   (declare (salience 50))
   (symptom (name weight-loss))
   => (bump-syndrome diabetes 0.3))

(defrule syn-diab-fatigue
   (declare (salience 50))
   (symptom (name fatigue))
   => (bump-syndrome diabetes 0.15))

;; --- Гипотиреоз ---
(defrule syn-hypo-cold
   (declare (salience 50))
   (symptom (name cold-intolerance))
   => (bump-syndrome hypothyroid 0.4))

(defrule syn-hypo-weightgain
   (declare (salience 50))
   (symptom (name weight-gain))
   => (bump-syndrome hypothyroid 0.35))

(defrule syn-hypo-fatigue
   (declare (salience 50))
   (symptom (name fatigue))
   => (bump-syndrome hypothyroid 0.25))