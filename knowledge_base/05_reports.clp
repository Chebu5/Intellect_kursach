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