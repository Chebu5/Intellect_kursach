;; ==========================================================
;; БАЗОВЫЕ ШАБЛОНЫ И ФУНКЦИИ
;; ==========================================================

(deftemplate patient
   (slot age (type INTEGER) (default 0))
   (slot sex (type SYMBOL) (default unknown))
   (slot pregnant (type SYMBOL) (default no)))

(deftemplate chronic-condition
   (slot name (type SYMBOL)))

(deftemplate symptom
   (slot name (type SYMBOL))
   (slot duration (type SYMBOL) (default unknown)))

(deftemplate syndrome
   (slot type (type SYMBOL))
   (slot cf (type FLOAT) (default 0.0)))

(deftemplate recommendation
   (slot specialist (type STRING))
   (slot cf (type FLOAT) (default 0.0))
   (slot urgency (type SYMBOL) (default routine)))

(deftemplate red-flag
   (slot name (type SYMBOL))
   (slot action (type STRING)))

(deftemplate modifier-applied
   (slot name (type SYMBOL)))

(deftemplate reported
   (slot what (type SYMBOL)))

;; ---------- ДЕФФУНКЦИИ ----------
(deffunction cf-combine (?cf1 ?cf2)
   "MYCIN-подобное комбинирование коэффициентов уверенности"
   (if (and (>= ?cf1 0) (>= ?cf2 0))
      then (return (+ ?cf1 (* ?cf2 (- 1 ?cf1)))))
   (if (and (< ?cf1 0) (< ?cf2 0))
      then (return (+ ?cf1 ?cf2 (* ?cf1 ?cf2))))
   (return (/ (+ ?cf1 ?cf2) (- 1 (min (abs ?cf1) (abs ?cf2))))))

(deffunction bump-syndrome (?type ?cf)
   "Добавить/усилить синдром"
   (if (<= ?cf 0) then (return))
   (bind ?existing (find-all-facts ((?s syndrome)) (eq ?s:type ?type)))
   (if (eq (length$ ?existing) 0)
      then (assert (syndrome (type ?type) (cf ?cf)))
      else
      (bind ?old (nth$ 1 ?existing))
      (bind ?oldcf (fact-slot-value ?old cf))
      (bind ?newcf (cf-combine ?oldcf ?cf))
      (if (> ?newcf (+ ?oldcf 0.001))
         then (modify ?old (cf ?newcf)))))

(deffunction syndrome-to-specialist (?type)
   (if (eq ?type cardiac)          then (return "КАРДИОЛОГ"))
   (if (eq ?type pulmonary)        then (return "ПУЛЬМОНОЛОГ"))
   (if (eq ?type gerd)             then (return "ГАСТРОЭНТЕРОЛОГ"))
   (if (eq ?type radiculopathy)    then (return "НЕВРОЛОГ"))
   (if (eq ?type migraine)         then (return "НЕВРОЛОГ"))
   (if (eq ?type tension-headache) then (return "НЕВРОЛОГ"))
   (if (eq ?type cluster-headache) then (return "НЕВРОЛОГ"))
   (if (eq ?type diabetes)         then (return "ЭНДОКРИНОЛОГ"))
   (if (eq ?type hypothyroid)      then (return "ЭНДОКРИНОЛОГ"))
   (if (eq ?type allergy)          then (return "АЛЛЕРГОЛОГ-ИММУНОЛОГ"))
   (if (eq ?type gyn)              then (return "ГИНЕКОЛОГ"))
   (if (eq ?type panic-disorder)   then (return "ПСИХОТЕРАПЕВТ"))
   (if (eq ?type depression)       then (return "ПСИХИАТР"))
   (if (eq ?type uti)              then (return "УРОЛОГ"))
   (if (eq ?type renal-colic)      then (return "УРОЛОГ"))
   (if (eq ?type derm-onco)        then (return "ДЕРМАТОЛОГ"))
   (return "ТЕРАПЕВТ"))

(deffunction syndrome-to-urgency (?type)
   (if (eq ?type cardiac)     then (return urgent))
   (if (eq ?type pulmonary)   then (return urgent))
   (if (eq ?type gyn)         then (return urgent))
   (if (eq ?type renal-colic) then (return urgent))
   (if (eq ?type derm-onco)   then (return urgent))
   (return routine))