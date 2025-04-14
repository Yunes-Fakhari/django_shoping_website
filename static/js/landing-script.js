// Shop Pages Slider //
var shopSlider = new Swiper(".shop-slider", {
    slidesPerView: 1.5,
    slidesPerGroup: 1,
    spaceBetween: 15,
    centeredSlides: true,
    loop: true,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
    breakpoints: {
        767: {
            slidesPerView: 3.8,
            spaceBetween: 30,
            slidesPerGroup: 3,
        },

        475: {

            slidesPerView: 2.5,
            slidesPerGroup: 3,

        }
    }
});

// Product Pages Slider //
var productPagesSlider = new Swiper(".product-pages-slider", {
    slidesPerView: 1.5,
    spaceBetween: 15,
    centeredSlides: true,
    loop: true,
    breakpoints: {
        1200: {
            spaceBetween: 30,
            slidesPerView: 2.2,
        },
        475: {
            spaceBetween: 15,
            slidesPerView: 2.2,
        }

    }

});

//  Tap To Top Js 
const tapTopBtn = document.querySelector(".tap-to-top-button")
const tapTopTopBox = document.querySelector(".tap-to-top-box")
tapTopBtn?.addEventListener("click", function () {
    window.scroll({
        top: 0,
        behavior: 'smooth'
    });

})
window.onscroll = function () {
    if (pageYOffset >= 1000) {
        tapTopTopBox.classList.remove("hide")
    } else {
        tapTopTopBox.classList.add("hide")
    }
}

// Header Menu Js //
const toggleBtn = document.querySelector(".sidebar-toggle");
const header = document.querySelector(".header")
toggleBtn.addEventListener("click", function () {
    header.classList.toggle("show")
})

//  Scroll Active // 
const sections = document.querySelectorAll("section");
const navLi = document.querySelectorAll(".navigation ul li");
window.addEventListener("scroll", () => {
    if (window.offsetTop === 0) {
        tapTopBtn.classList.add("hide")
    }
    let current = "";
    sections.forEach((section) => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - sectionHeight / 3) {
            current = section.getAttribute("id") == null ? current : section.getAttribute("id");
        }
    });
    navLi.forEach((el) => {
        if (el.classList.contains(current)) {
            el.classList.add("active");
        } else {
            el.classList.remove("active");
        }
    });
});

