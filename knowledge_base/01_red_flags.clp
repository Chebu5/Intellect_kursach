;; ==========================================================
;; УРОВЕНЬ 1. КРАСНЫЕ ФЛАГИ (salience 100)
;; ==========================================================

(defrule rf-chest-cardiac
   (declare (salience 100))
   (symptom (name chest-pain))
   (symptom (name dyspnea))
   (not (red-flag (name possible-mi)))
   =>
   (assert (red-flag (name possible-mi) (action "ВЫЗВАТЬ СКОРУЮ: возможен инфаркт миокарда"))))

(defrule rf-thunderclap
   (declare (salience 100))
   (symptom (name headache))
   (symptom (name sudden-onset))
   (not (red-flag (name possible-sah)))
   =>
   (assert (red-flag (name possible-sah) (action "ВЫЗВАТЬ СКОРУЮ: внезапная сильнейшая головная боль (САК/инсульт)"))))

(defrule rf-abdomen-rigid
   (declare (salience 100))
   (symptom (name abdomen-pain))
   (symptom (name abdomen-rigid))
   (not (red-flag (name acute-abdomen)))
   =>
   (assert (red-flag (name acute-abdomen) (action "СРОЧНО В ХИРУРГИЮ: признаки острого живота"))))

(defrule rf-anaphylaxis
   (declare (salience 100))
   (symptom (name skin-rash))
   (symptom (name dyspnea))
   (symptom (name throat-swelling))
   (not (red-flag (name anaphylaxis)))
   =>
   (assert (red-flag (name anaphylaxis) (action "ВЫЗВАТЬ СКОРУЮ: анафилаксия, адреналин"))))

(defrule rf-stroke-fast
   (declare (salience 100))
   (symptom (name facial-droop))
   (symptom (name arm-weakness))
   (symptom (name speech-difficulty))
   (not (red-flag (name stroke)))
   =>
   (assert (red-flag (name stroke) (action "ВЫЗВАТЬ СКОРУЮ: признаки инсульта (FAST)"))))

(defrule rf-obstetric-bleeding
   (declare (salience 100))
   (patient (pregnant yes))
   (symptom (name vaginal-bleeding))
   (not (red-flag (name obstetric-emergency)))
   =>
   (assert (red-flag (name obstetric-emergency) (action "СРОЧНО: акушерское кровотечение"))))

(defrule rf-suicidal
   (declare (salience 100))
   (symptom (name suicidal-thoughts))
   (not (red-flag (name psychiatric-emergency)))
   =>
   (assert (red-flag (name psychiatric-emergency) (action "СРОЧНО: суицидальные мысли"))))

(defrule rf-hyperglycemia
   (declare (salience 100))
   (symptom (name polyuria))
   (symptom (name polydipsia))
   (symptom (name confusion))
   (not (red-flag (name hhs-dka)))
   =>
   (assert (red-flag (name hhs-dka) (action "СРОЧНО: гипергликемическая декомпенсация"))))

(defrule rf-sepsis
   (declare (salience 100))
   (symptom (name fever))
   (symptom (name confusion))
   (not (red-flag (name sepsis)))
   =>
   (assert (red-flag (name sepsis) (action "ВЫЗВАТЬ СКОРУЮ: возможен сепсис"))))