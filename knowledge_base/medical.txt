;; ==========================================================
;; МЕДИЦИНСКАЯ ЭКСПЕРТНАЯ СИСТЕМА — ГИБКАЯ ДИФФЕРЕНЦИАЛЬНАЯ ДИАГНОСТИКА
;; Уровни: симптомы -> синдромы (накопление улик) -> рекомендации -> отчёт
;; ==========================================================

;; ---------- ШАБЛОНЫ ----------
(deftemplate patient
   (slot age (type INTEGER) (default 0))
   (slot sex (type SYMBOL) (default unknown))
   (slot pregnant (type SYMBOL) (default no)))

(deftemplate chronic-condition
   (slot name (type SYMBOL)))

(deftemplate symptom
   (slot name (type SYMBOL))
   (slot severity (type INTEGER) (default 5))
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

;; ==========================================================
;; УРОВЕНЬ 1. КРАСНЫЕ ФЛАГИ (salience 100)
;; ==========================================================
(defrule rf-chest-cardiac
   (declare (salience 100))
   (symptom (name chest-pain) (severity ?s&:(>= ?s 7)))
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

;; ==========================================================
;; УРОВЕНЬ 2. НАКОПЛЕНИЕ УЛИК (salience 50)
;; ==========================================================

;; --- КАРДИОЛОГИЯ ---
(defrule syn-cardiac-pain-severe
   (declare (salience 50))
   (symptom (name chest-pain) (severity ?s&:(>= ?s 7)))
   => (bump-syndrome cardiac 0.4))
(defrule syn-cardiac-pain-mild
   (declare (salience 50))
   (symptom (name chest-pain) (severity ?s&:(< ?s 7)))
   => (bump-syndrome cardiac 0.2))
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

;; --- ПУЛЬМОНОЛОГИЯ ---
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

;; --- ГАСТРОЭНТЕРОЛОГИЯ (ГЭРБ) ---
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

;; --- НЕВРОЛОГИЯ: Радикулопатия ---
(defrule syn-radic-back
   (declare (salience 50))
   (symptom (name back-pain))
   => (bump-syndrome radiculopathy 0.3))
(defrule syn-radic-leg
   (declare (salience 50))
   (symptom (name leg-radiation))
   => (bump-syndrome radiculopathy 0.45))
(defrule syn-radic-numb
   (declare (salience 50))
   (symptom (name numbness))
   => (bump-syndrome radiculopathy 0.25))
(defrule syn-radic-weak
   (declare (salience 50))
   (symptom (name muscle-weakness))
   => (bump-syndrome radiculopathy 0.35))

;; --- НЕВРОЛОГИЯ: Мигрень ---
(defrule syn-migr-headache
   (declare (salience 50))
   (symptom (name headache))
   => (bump-syndrome migraine 0.25))
(defrule syn-migr-photo
   (declare (salience 50))
   (symptom (name photophobia))
   => (bump-syndrome migraine 0.35))
(defrule syn-migr-nausea
   (declare (salience 50))
   (symptom (name nausea))
   => (bump-syndrome migraine 0.2))
(defrule syn-migr-aura
   (declare (salience 50))
   (symptom (name visual-aura))
   => (bump-syndrome migraine 0.5))

;; --- НЕВРОЛОГИЯ: ГБН (Тензионная) ---
(defrule syn-tension-headache
   (declare (salience 50))
   (symptom (name headache))
   (not (symptom (name photophobia))) ; Только если нет светобоязни
   => (bump-syndrome tension-headache 0.3))
(defrule syn-tension-stress
   (declare (salience 50))
   (symptom (name stress))
   (not (symptom (name photophobia)))
   => (bump-syndrome tension-headache 0.35))

;; --- НЕВРОЛОГИЯ: Кластерная ---
(defrule syn-cluster-eye
   (declare (salience 50))
   (symptom (name eye-pain))
   => (bump-syndrome cluster-headache 0.4))
(defrule syn-cluster-nasal
   (declare (salience 50))
   (symptom (name nasal-congestion))
   => (bump-syndrome cluster-headache 0.3))

;; --- ЭНДОКРИНОЛОГИЯ: Диабет ---
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

;; --- ЭНДОКРИНОЛОГИЯ: Гипотиреоз ---
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

;; --- АЛЛЕРГОЛОГИЯ ---
(defrule syn-allergy-rash
   (declare (salience 50))
   (symptom (name skin-rash))
   => (bump-syndrome allergy 0.3))
(defrule syn-allergy-itch
   (declare (salience 50))
   (symptom (name itching))
   => (bump-syndrome allergy 0.3))
(defrule syn-allergy-contact
   (declare (salience 50))
   (symptom (name after-contact))
   => (bump-syndrome allergy 0.45))

;; --- ДЕРМАТОЛОГИЯ ---
(defrule syn-derm-mole
   (declare (salience 50))
   (symptom (name mole-change))
   => (bump-syndrome derm-onco 0.8))

;; --- ГИНЕКОЛОГИЯ ---
(defrule syn-gyn-lower-pain
   (declare (salience 50))
   (symptom (name lower-abdomen-pain))
   => (bump-syndrome gyn 0.35))
(defrule syn-gyn-discharge
   (declare (salience 50))
   (symptom (name vaginal-discharge))
   => (bump-syndrome gyn 0.4))
(defrule syn-gyn-bleeding
   (declare (salience 50))
   (symptom (name vaginal-bleeding))
   => (bump-syndrome gyn 0.5))

;; --- ПСИХИАТРИЯ: Паника ---
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

;; --- ПСИХИАТРИЯ: Депрессия ---
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

;; --- УРОЛОГИЯ: ИМП ---
(defrule syn-uti-dysuria
   (declare (salience 50))
   (symptom (name dysuria))
   => (bump-syndrome uti 0.5))
(defrule syn-uti-polyuria
   (declare (salience 50))
   (symptom (name polyuria))
   => (bump-syndrome uti 0.3))
(defrule syn-uti-fever
   (declare (salience 50))
   (symptom (name fever))
   => (bump-syndrome uti 0.2))

;; --- УРОЛОГИЯ: МКБ (Почечная колика) ---
(defrule syn-renal-flank
   (declare (salience 50))
   (symptom (name flank-pain))
   => (bump-syndrome renal-colic 0.6))
(defrule syn-renal-hematuria
   (declare (salience 50))
   (symptom (name hematuria))
   => (bump-syndrome renal-colic 0.5))

;; ==========================================================
;; УРОВЕНЬ 3. МОДИФИКАТОРЫ КОНТЕКСТА (salience 40)
;; Работают ТОЛЬКО если синдром уже подозревается (cf > 0)
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

;; ==========================================================
;; УРОВЕНЬ 6. ОТЧЁТЫ (salience < 0)
;; ==========================================================
(defrule report-emergency
   (declare (salience -90))
   (exists (red-flag))
   (not (reported (what emergency)))
   =>
   (printout t "!!! ВНИМАНИЕ! ОБНАРУЖЕНЫ КРАСНЫЕ ФЛАГИ:" crlf)
   (do-for-all-facts ((?rf red-flag)) (eq 1 1)
      (printout t "  - " ?rf:action crlf))
   (assert (reported (what emergency))))

(defrule report-diagnosis
   (declare (salience -100))
   (recommendation (specialist ?s) (cf ?cf) (urgency ?u))
   (not (recommendation (specialist ?s2) (cf ?cf2&:(> ?cf2 ?cf))))
   (not (reported (what diagnosis)))
   =>
   (printout t crlf "РЕКОМЕНДАЦИЯ: " ?s crlf
              "УВЕРЕННОСТЬ: " (round (* 100 ?cf)) "%" crlf
              "СРОЧНОСТЬ: " ?u crlf)
   (assert (reported (what diagnosis))))

(defrule report-fallback
   (declare (salience -110))
   (not (recommendation))
   (not (red-flag))
   (not (reported (what diagnosis)))
   =>
   (printout t "Недостаточно данных для гипотезы. Рекомендован терапевт." crlf)
   (assert (reported (what diagnosis))))