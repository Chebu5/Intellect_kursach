;; ==========================================================
;; МЕДИЦИНСКАЯ ЭКСПЕРТНАЯ СИСТЕМА — МНОГОУРОВНЕВЫЙ ВЫВОД
;; Уровни: симптомы -> синдромы -> рекомендации -> отчёт
;; Коэффициенты уверенности (MYCIN-подобная алгебра)
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
      then
      (return (+ ?cf1 (* ?cf2 (- 1 ?cf1)))))
   (if (and (< ?cf1 0) (< ?cf2 0))
      then
      (return (+ ?cf1 ?cf2 (* ?cf1 ?cf2))))
   (return (/ (+ ?cf1 ?cf2) (- 1 (min (abs ?cf1) (abs ?cf2))))))

(deffunction bump-syndrome (?type ?cf)
   "Добавить/усилить синдром (без циклов на малых приращениях)"
   (if (<= ?cf 0)
      then
      (return))
   (bind ?existing (find-all-facts ((?s syndrome)) (eq ?s:type ?type)))
   (if (eq (length$ ?existing) 0)
      then
      (assert (syndrome (type ?type) (cf ?cf)))
      else
      (bind ?old (nth$ 1 ?existing))
      (bind ?oldcf (fact-slot-value ?old cf))
      (bind ?newcf (cf-combine ?oldcf ?cf))
      (if (> ?newcf (+ ?oldcf 0.001))
         then
         (modify ?old (cf ?newcf)))))

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
   (assert (red-flag (name possible-mi)
                     (action "ВЫЗВАТЬ СКОРУЮ: возможен инфаркт миокарда"))))

(defrule rf-thunderclap
   (declare (salience 100))
   (symptom (name headache) (severity ?s&:(>= ?s 9)))
   (symptom (name sudden-onset))
   (not (red-flag (name possible-sah)))
   =>
   (assert (red-flag (name possible-sah)
                     (action "ВЫЗВАТЬ СКОРУЮ: возможен инсульт/САК (внезапная сильнейшая головная боль)"))))

(defrule rf-abdomen-rigid
   (declare (salience 100))
   (symptom (name abdomen-pain) (severity ?s&:(>= ?s 7)))
   (symptom (name abdomen-rigid))
   (not (red-flag (name acute-abdomen)))
   =>
   (assert (red-flag (name acute-abdomen)
                     (action "СРОЧНО В ХИРУРГИЮ: признаки острого живота"))))

(defrule rf-anaphylaxis
   (declare (salience 100))
   (symptom (name skin-rash))
   (symptom (name dyspnea))
   (symptom (name throat-swelling))
   (not (red-flag (name anaphylaxis)))
   =>
   (assert (red-flag (name anaphylaxis)
                     (action "ВЫЗВАТЬ СКОРУЮ: анафилаксия, адреналин"))))

(defrule rf-stroke-fast
   (declare (salience 100))
   (symptom (name facial-droop))
   (symptom (name arm-weakness))
   (symptom (name speech-difficulty))
   (not (red-flag (name stroke)))
   =>
   (assert (red-flag (name stroke)
                     (action "ВЫЗВАТЬ СКОРУЮ: признаки инсульта (FAST)"))))

(defrule rf-obstetric-bleeding
   (declare (salience 100))
   (patient (pregnant yes))
   (symptom (name vaginal-bleeding))
   (not (red-flag (name obstetric-emergency)))
   =>
   (assert (red-flag (name obstetric-emergency)
                     (action "СРОЧНО: акушерское кровотечение"))))

(defrule rf-suicidal
   (declare (salience 100))
   (symptom (name suicidal-thoughts))
   (not (red-flag (name psychiatric-emergency)))
   =>
   (assert (red-flag (name psychiatric-emergency)
                     (action "СРОЧНО: суицидальные мысли — психиатрическая экстренность"))))

(defrule rf-hyperglycemia
   (declare (salience 100))
   (symptom (name polyuria) (severity ?s&:(>= ?s 8)))
   (symptom (name polydipsia))
   (symptom (name confusion))
   (not (red-flag (name hhs-dka)))
   =>
   (assert (red-flag (name hhs-dka)
                     (action "СРОЧНО: гипергликемическая декомпенсация"))))

;; ==========================================================
;; УРОВЕНЬ 2. РАСПОЗНАВАНИЕ СИНДРОМОВ (salience 50)
;; ==========================================================

;; --- Кардиальный ---
(defrule syn-cardiac-radiation
   (declare (salience 50))
   (symptom (name chest-pain))
   (symptom (name chest-radiation))
   =>
   (bump-syndrome cardiac 0.6))

(defrule syn-cardiac-dyspnea
   (declare (salience 50))
   (symptom (name chest-pain))
   (symptom (name dyspnea))
   (patient (age ?a&:(>= ?a 50)))
   =>
   (bump-syndrome cardiac 0.4))

(defrule syn-cardiac-risk
   (declare (salience 50))
   (symptom (name chest-pain))
   (chronic-condition (name diabetes))
   =>
   (bump-syndrome cardiac 0.3))

(defrule syn-cardiac-htn
   (declare (salience 50))
   (symptom (name chest-pain))
   (chronic-condition (name hypertension))
   =>
   (bump-syndrome cardiac 0.25))

(defrule syn-cardiac-vegetative
   (declare (salience 50))
   (symptom (name chest-pain))
   (symptom (name sweating))
   (symptom (name nausea))
   =>
   (bump-syndrome cardiac 0.3))

;; --- Пульмонологический ---
(defrule syn-pulmo-pleuritic
   (declare (salience 50))
   (symptom (name chest-pain))
   (symptom (name worse-on-inspiration))
   =>
   (bump-syndrome pulmonary 0.5))

(defrule syn-pulmo-infection
   (declare (salience 50))
   (symptom (name cough))
   (symptom (name fever))
   (symptom (name dyspnea))
   =>
   (bump-syndrome pulmonary 0.6))

(defrule syn-pulmo-asthma
   (declare (salience 50))
   (chronic-condition (name asthma))
   (symptom (name wheezing))
   =>
   (bump-syndrome pulmonary 0.7))

;; --- ГЭРБ ---
(defrule syn-gerd-classic
   (declare (salience 50))
   (symptom (name heartburn))
   (symptom (name sour-taste))
   =>
   (bump-syndrome gerd 0.7))

(defrule syn-gerd-atypical
   (declare (salience 50))
   (symptom (name chest-pain))
   (symptom (name worse-after-meals))
   (symptom (name heartburn))
   =>
   (bump-syndrome gerd 0.5))

;; --- Радикулопатия ---
(defrule syn-radic
   (declare (salience 50))
   (symptom (name back-pain))
   (symptom (name leg-radiation))
   (symptom (name numbness))
   =>
   (bump-syndrome radiculopathy 0.7))

(defrule syn-radic-weakness
   (declare (salience 50))
   (symptom (name back-pain))
   (symptom (name leg-radiation))
   (symptom (name muscle-weakness))
   =>
   (bump-syndrome radiculopathy 0.8))

;; --- Мигрень ---
(defrule syn-migraine
   (declare (salience 50))
   (symptom (name headache))
   (symptom (name photophobia))
   (symptom (name nausea))
   =>
   (bump-syndrome migraine 0.75))

(defrule syn-migraine-aura
   (declare (salience 50))
   (symptom (name headache))
   (symptom (name visual-aura))
   =>
   (bump-syndrome migraine 0.7))

;; --- ГБН ---
(defrule syn-tension
   (declare (salience 50))
   (symptom (name headache))
   (symptom (name stress))
   (not (symptom (name photophobia)))
   =>
   (bump-syndrome tension-headache 0.55))

;; --- Кластерная ---
(defrule syn-cluster
   (declare (salience 50))
   (symptom (name headache))
   (symptom (name eye-pain))
   (symptom (name nasal-congestion))
   =>
   (bump-syndrome cluster-headache 0.7))

;; --- Диабет ---
(defrule syn-diabetes-classic
   (declare (salience 50))
   (symptom (name polyuria))
   (symptom (name polydipsia))
   (symptom (name weight-loss))
   =>
   (bump-syndrome diabetes 0.85))

(defrule syn-diabetes-partial
   (declare (salience 50))
   (symptom (name polyuria))
   (symptom (name polydipsia))
   (not (symptom (name weight-loss)))
   =>
   (bump-syndrome diabetes 0.5))

;; --- Гипотиреоз ---
(defrule syn-hypothyroid
   (declare (salience 50))
   (symptom (name cold-intolerance))
   (symptom (name weight-gain))
   (symptom (name fatigue))
   =>
   (bump-syndrome hypothyroid 0.6))

;; --- Аллергия ---
(defrule syn-allergy
   (declare (salience 50))
   (symptom (name skin-rash))
   (symptom (name itching))
   (symptom (name after-contact))
   =>
   (bump-syndrome allergy 0.8))

;; --- Дерматоонкология ---
(defrule syn-derm-mole
   (declare (salience 50))
   (symptom (name mole-change))
   =>
   (bump-syndrome derm-onco 0.7))

;; --- Гинекология ---
(defrule syn-gyn
   (declare (salience 50))
   (patient (sex female))
   (symptom (name lower-abdomen-pain))
   (symptom (name vaginal-discharge))
   =>
   (bump-syndrome gyn 0.65))

;; --- Паника ---
(defrule syn-panic
   (declare (salience 50))
   (symptom (name panic-attack))
   (symptom (name palpitations))
   =>
   (bump-syndrome panic-disorder 0.7))

;; --- Депрессия ---
(defrule syn-depression
   (declare (salience 50))
   (symptom (name low-mood))
   (symptom (name anhedonia))
   (symptom (name insomnia))
   =>
   (bump-syndrome depression 0.75))

;; --- ИМП / МКБ ---
(defrule syn-uti
   (declare (salience 50))
   (symptom (name dysuria))
   (symptom (name polyuria))
   (symptom (name fever))
   =>
   (bump-syndrome uti 0.6))

(defrule syn-renal-colic
   (declare (salience 50))
   (symptom (name flank-pain) (severity ?s&:(>= ?s 7)))
   (symptom (name hematuria))
   =>
   (bump-syndrome renal-colic 0.75))

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
   (bump-syndrome gyn 0.5))

(defrule mod-elderly-cardiac
   (declare (salience 40))
   (patient (age ?a&:(>= ?a 65)))
   (syndrome (type cardiac))
   (not (modifier-applied (name mod-elderly-cardiac)))
   =>
   (assert (modifier-applied (name mod-elderly-cardiac)))
   (bump-syndrome cardiac 0.15))

(defrule mod-male-cardiac
   (declare (salience 40))
   (patient (sex male) (age ?a&:(>= ?a 45)))
   (syndrome (type cardiac))
   (not (modifier-applied (name mod-male-cardiac)))
   =>
   (assert (modifier-applied (name mod-male-cardiac)))
   (bump-syndrome cardiac 0.1))

(defrule mod-diabetes-cardiac
   (declare (salience 40))
   (chronic-condition (name diabetes))
   (syndrome (type cardiac))
   (not (modifier-applied (name mod-diabetes-cardiac)))
   =>
   (assert (modifier-applied (name mod-diabetes-cardiac)))
   (bump-syndrome cardiac 0.15))

(defrule mod-smoker-pulmo
   (declare (salience 40))
   (chronic-condition (name smoker))
   (syndrome (type pulmonary))
   (not (modifier-applied (name mod-smoker-pulmo)))
   =>
   (assert (modifier-applied (name mod-smoker-pulmo)))
   (bump-syndrome pulmonary 0.1))

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
   (bind ?recs (find-all-facts ((?r recommendation))
                   (eq ?r:specialist ?spec)))
   (if (eq (length$ ?recs) 0)
      then
      (assert (recommendation (specialist ?spec) (cf ?cf) (urgency ?urg)))
      else
      (bind ?r (nth$ 1 ?recs))
      (bind ?existing-cf (fact-slot-value ?r cf))
      (if (> ?cf ?existing-cf)
         then
         (modify ?r (cf ?cf)))))

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
   (printout t crlf
              "РЕКОМЕНДАЦИЯ: " ?s crlf
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