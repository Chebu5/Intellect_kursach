;; ==========================================================
;; УРОВЕНЬ 2. НЕВРОЛОГИЯ (salience 50)
;; ==========================================================

;; --- Радикулопатия ---
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

;; --- Мигрень ---
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

;; --- ГБН (Тензионная) ---
(defrule syn-tension-headache
   (declare (salience 50))
   (symptom (name headache))
   (not (symptom (name photophobia)))
   => (bump-syndrome tension-headache 0.3))

(defrule syn-tension-stress
   (declare (salience 50))
   (symptom (name stress))
   (not (symptom (name photophobia)))
   => (bump-syndrome tension-headache 0.35))

;; --- Кластерная ---
(defrule syn-cluster-eye
   (declare (salience 50))
   (symptom (name eye-pain))
   => (bump-syndrome cluster-headache 0.4))

(defrule syn-cluster-nasal
   (declare (salience 50))
   (symptom (name nasal-congestion))
   => (bump-syndrome cluster-headache 0.3))