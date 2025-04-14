/*=====================
  Active Class Remove js
  ==========================*/

/// Common Template ///
const toggleClassF = function (element) {
    if (element) {
        element.forEach(el => {
            const childEl = el.children;
            [...childEl].forEach((clE) => {
                clE.addEventListener("click", function () {
                    const allChildren = this.parentElement.children;
                    [...allChildren].forEach((el) => {
                        el.classList.remove("active");
                    })
                    this.classList.add("active");
                });
            });
        })
    }
}

/// Color ///
const colorList = document.querySelectorAll(".color-list");
toggleClassF(colorList);

/// Size
const sizeList = document.querySelectorAll(".size-list");
toggleClassF(sizeList);

/// Shop Page Color List
const shopColorLis = document.querySelectorAll(".filter-color");
toggleClassF(shopColorLis);






