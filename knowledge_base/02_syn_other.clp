;; ==========================================================
;; УРОВЕНЬ 2. ПРОЧИЕ СПЕЦИАЛЬНОСТИ (salience 50)
;; ==========================================================

;; --- Аллергология ---
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

;; --- Дерматология ---
(defrule syn-derm-mole
   (declare (salience 50))
   (symptom (name mole-change))
   => (bump-syndrome derm-onco 0.8))

;; --- Гинекология ---
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