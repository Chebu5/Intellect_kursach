;; ==========================================================
;; УРОВЕНЬ 3. МОДИФИКАТОРЫ КОНТЕКСТА (salience 40)
;; ==========================================================

(defrule mod-pregnancy-gyn
   (declare (salience 40))
   (patient (pregnant yes))
   (symptom (name abdomen-pain))
   (not (modifier-applied (name mod-pregnancy-gyn)))
   =>
   (assert (modifier-applied (name mod-pregnancy-gyn)))
   (bump-syndrome gyn 0.4))

(defrule mod-elderly-cardiac
   (declare (salience 40))
   (patient (age ?a&:(>= ?a 65)))
   (syndrome (type cardiac) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-elderly-cardiac)))
   =>
   (assert (modifier-applied (name mod-elderly-cardiac)))
   (bump-syndrome cardiac 0.15))

(defrule mod-male-cardiac
   (declare (salience 40))
   (patient (sex male) (age ?a&:(>= ?a 45)))
   (syndrome (type cardiac) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-male-cardiac)))
   =>
   (assert (modifier-applied (name mod-male-cardiac)))
   (bump-syndrome cardiac 0.1))

(defrule mod-diabetes-cardiac
   (declare (salience 40))
   (chronic-condition (name diabetes))
   (syndrome (type cardiac) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-diabetes-cardiac)))
   =>
   (assert (modifier-applied (name mod-diabetes-cardiac)))
   (bump-syndrome cardiac 0.15))

(defrule mod-htn-cardiac
   (declare (salience 40))
   (chronic-condition (name hypertension))
   (syndrome (type cardiac) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-htn-cardiac)))
   =>
   (assert (modifier-applied (name mod-htn-cardiac)))
   (bump-syndrome cardiac 0.15))

(defrule mod-smoker-pulmo
   (declare (salience 40))
   (chronic-condition (name smoker))
   (syndrome (type pulmonary) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-smoker-pulmo)))
   =>
   (assert (modifier-applied (name mod-smoker-pulmo)))
   (bump-syndrome pulmonary 0.15))

(defrule mod-asthma-pulmo
   (declare (salience 40))
   (chronic-condition (name asthma))
   (syndrome (type pulmonary) (cf ?cf&:(> ?cf 0)))
   (not (modifier-applied (name mod-asthma-pulmo)))
   =>
   (assert (modifier-applied (name mod-asthma-pulmo)))
   (bump-syndrome pulmonary 0.3))

(defrule mod-anticoagulant-bleeding
   (declare (salience 40))
   (chronic-condition (name anticoagulants))
   (symptom (name vaginal-bleeding))
   (not (modifier-applied (name mod-anticoagulant-bleeding)))
   =>
   (assert (modifier-applied (name mod-anticoagulant-bleeding)))
   (bump-syndrome gyn 0.3))