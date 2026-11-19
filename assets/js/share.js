function hide_() {
  var boto = document.getElementById("boto-compartir");
  let btn_tooltip = bootstrap.Tooltip.getInstance(boto);
  btn_tooltip.hide();
}
function copy() {
  var text = document
    .getElementById("boto-compartir")
    .getAttribute("data-enllac");
  console.log(text);
  navigator.clipboard.writeText(text);
  setTimeout(hide_, 1500);
}

// init tooltips
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
);

document.getElementById("boto-compartir").addEventListener("click", copy);
