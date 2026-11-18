;; ==========================================================
;; УРОВЕНЬ 4. ПРОДВИЖЕНИЕ СИНДРОМОВ (salience 20)
;; ==========================================================
(defrule promote-syndrome
   (declare (salience 20))
   (syndrome (type ?t) (cf ?cf&:(>= ?cf 0.4)))
   =>
   (bind ?spec (syndrome-to-specialist ?t))
   (bind ?urg  (syndrome-to-urgency ?t))
   (bind ?recs (find-all-facts ((?r recommendation)) (eq ?r:specialist ?spec)))
   (if (eq (length$ ?recs) 0)
      then (assert (recommendation (specialist ?spec) (cf ?cf) (urgency ?urg)))
      else
      (bind ?r (nth$ 1 ?recs))
      (bind ?existing-cf (fact-slot-value ?r cf))
      (if (> ?cf ?existing-cf)
         then (modify ?r (cf ?cf)))))

;; ==========================================================
;; УРОВЕНЬ 5. ДИФФЕРЕНЦИАЛЬНАЯ ДИАГНОСТИКА (salience 15)
;; ==========================================================
(defrule competing-syndromes
   (declare (salience 15))
   (syndrome (type ?t1) (cf ?cf1&:(>= ?cf1 0.4)))
   (syndrome (type ?t2) (cf ?cf2&:(>= ?cf2 0.4)))
   (test (neq ?t1 ?t2))
   (test (< (abs (- ?cf1 ?cf2)) 0.2))
   (not (recommendation (specialist "ТЕРАПЕВТ")))
   =>
   (bind ?newcf (* 0.5 (min ?cf1 ?cf2)))
   (assert (recommendation (specialist "ТЕРАПЕВТ") (cf ?newcf) (urgency routine))))