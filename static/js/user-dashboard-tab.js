
/*=====================
   User Dashboard js
 ==========================*/

const tabBoxEl = document.querySelectorAll(".option-wrap .tab-box");
const btnLink = document.querySelectorAll(".nav-tabs .nav-link");

btnLink.forEach(el => {
    el.addEventListener("click", function () {
        window.scroll({
            top: 0,
            behavior: 'smooth'
        });

    })
})

tabBoxEl.forEach(function (el) {
    el.addEventListener("click", function () {
        const boxData = this.getAttribute('data-class')
        btnLink.forEach(function (el) {
            const activeEl = el.getAttribute('aria-controls')

            if (activeEl === boxData) {
                el.click();
            }
        })
    })
})


const productElementTab = document.querySelectorAll("[data-productDetail='product-detail']");
const tabElement = document.querySelectorAll(".tab-pane");
const orderSidebarlink = document.querySelector("#orders-tab");

const tabRemoveClassFunction = function (tabHtmlElement) {
    tabHtmlElement.forEach(tabEl => {
        tabEl.classList.remove("show", "active")
    })
}
productElementTab.forEach(el => {
    el.addEventListener("click", function () {
        tabRemoveClassFunction(tabElement)
        const orderDetailTab = document.querySelector("#orders-details");
        orderDetailTab.classList.add("show", "active");
    })
});
orderSidebarlink.addEventListener("click", function () {
    tabRemoveClassFunction(tabElement);
    const orderTabContentEl = document.querySelector("#orders")
    orderTabContentEl.classList.add("show", "active");
})
