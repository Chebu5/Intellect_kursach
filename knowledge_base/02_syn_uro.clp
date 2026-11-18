;; ==========================================================
;; УРОВЕНЬ 2. УРОЛОГИЯ (salience 50)
;; ==========================================================

;; --- ИМП ---
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

;; --- МКБ (Почечная колика) ---
(defrule syn-renal-flank
   (declare (salience 50))
   (symptom (name flank-pain))
   => (bump-syndrome renal-colic 0.6))

(defrule syn-renal-hematuria
   (declare (salience 50))
   (symptom (name hematuria))
   => (bump-syndrome renal-colic 0.5))