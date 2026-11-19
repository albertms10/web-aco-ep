function reverseAnimation() {
  var ev = document.getElementById("llufa");
  ev.classList.remove("mostra-llufa");
  ev.offsetWidth;
  ev.classList.add("amaga-llufa");
  ev.style.display = "none";

  var ev = document.getElementById("innocentada-article");
  ev.classList.remove("amaga-article");
  ev.offsetWidth;
  ev.classList.add("mostra-article");
}

document.getElementById("llufa")?.addEventListener("click", reverseAnimation);
