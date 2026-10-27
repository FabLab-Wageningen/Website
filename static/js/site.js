// Small helpers for the menu and the open inloop dates. The site works
// without this file too; it only makes things nicer.

// Mobile menu button
var menuButton = document.querySelector(".menu-button");
var nav = document.getElementById("site-nav");
if (menuButton && nav) {
  menuButton.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

// Dropdowns ("Apparatuur") open on click as well as on hover
document.querySelectorAll(".sub-toggle").forEach(function (button) {
  button.addEventListener("click", function () {
    var item = button.parentElement;
    var open = item.classList.toggle("open");
    button.setAttribute("aria-expanded", open ? "true" : "false");
  });
});
document.addEventListener("click", function (event) {
  document.querySelectorAll(".has-sub.open").forEach(function (item) {
    if (!item.contains(event.target)) {
      item.classList.remove("open");
      item.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
    }
  });
});

// Hide open inloop dates that have passed, in case the site was not
// rebuilt since. Dates are compared in the visitor's own time zone.
var now = new Date();
var today = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
document.querySelectorAll("[data-dates]").forEach(function (list) {
  var shown = 0;
  list.querySelectorAll("[data-date]").forEach(function (item) {
    if (item.getAttribute("data-date") < today) item.hidden = true;
    else shown++;
  });
  var empty = list.nextElementSibling;
  if (empty && empty.classList.contains("no-dates")) empty.hidden = shown > 0;
});
