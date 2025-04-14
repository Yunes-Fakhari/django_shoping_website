/*=====================
  Search 3 Js 
==========================*/
let searchButtonEl = document.querySelector(".search");
let closeButtonEl = document.querySelector(".close-b");
let searchFullEl = document.querySelector(".header-center");

searchButtonEl.addEventListener("click", function () {
  searchFullEl.classList.add("show");
});
closeButtonEl.addEventListener("click", function () {
  searchFullEl.classList.remove("show");
});