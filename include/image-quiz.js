<script>
/*
 * Klickbare Bild-Kacheln für Quiz-Fragen.
 * Jede Kachel (.image-quiz-item) lässt sich per Klick an-/abwählen
 * (Klasse "selected"). Ein Klick auf ".image-quiz-check-btn" vergleicht die
 * Auswahl mit dem Attribut data-correct="true"/"false" jeder Kachel, färbt
 * sie entsprechend ein und zeigt die Trefferquote an.
 * ".image-quiz-reset-btn" setzt die Kacheln wieder zurück.
 */
document.addEventListener("DOMContentLoaded", function () {
  var quizzes = document.getElementsByClassName("image-quiz");

  for (var q = 0; q < quizzes.length; q++) {
    (function (quiz) {
      var items = quiz.getElementsByClassName("image-quiz-item");
      var checkBtn = quiz.querySelector(".image-quiz-check-btn");
      var resetBtn = quiz.querySelector(".image-quiz-reset-btn");
      var result = quiz.querySelector(".image-quiz-result");
      var checked = false;

      var i;
      for (i = 0; i < items.length; i++) {
        items[i].setAttribute("aria-pressed", "false");
        items[i].addEventListener("click", function () {
          if (checked) return;
          var isSelected = this.classList.toggle("selected");
          this.setAttribute("aria-pressed", isSelected ? "true" : "false");
        });
      }

      if (checkBtn) {
        checkBtn.addEventListener("click", function () {
          var correctCount = 0;
          for (var j = 0; j < items.length; j++) {
            var item = items[j];
            var isCorrect = item.dataset.correct === "true";
            var isSelected = item.classList.contains("selected");
            item.classList.remove("image-quiz-correct", "image-quiz-incorrect");
            if (isSelected === isCorrect) {
              item.classList.add("image-quiz-correct");
              correctCount++;
            } else {
              item.classList.add("image-quiz-incorrect");
            }
          }
          checked = true;
          if (result) {
            result.textContent = correctCount + " von " + items.length + " Diagrammen richtig beurteilt.";
          }
          checkBtn.disabled = true;
        });
      }

      if (resetBtn) {
        resetBtn.addEventListener("click", function () {
          for (var k = 0; k < items.length; k++) {
            items[k].classList.remove("selected", "image-quiz-correct", "image-quiz-incorrect");
            items[k].setAttribute("aria-pressed", "false");
          }
          if (result) {
            result.textContent = "";
          }
          checked = false;
          if (checkBtn) checkBtn.disabled = false;
        });
      }
    })(quizzes[q]);
  }
});
</script>
