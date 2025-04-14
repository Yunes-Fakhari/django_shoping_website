/*-----------------------------------------------------------------------------------

    Template Name:Oslo Theme
    Template URI: themes.pixelstrap.com/Oslo-Theme
    Description: This is Eccomerce Html Template
    Author: Pixelstrap
    Author URL: https://themeforest.net/user/pixelstrap

----------------------------------------------------------------------------------- */


// 01.Loader js
// 02.Ratio js 
// 03.Language And Unit Select js
// 04.Cart Mobile js
// 05.Plus Minus Item  Js
// 06.Footer Accordion Js 
// 07.Thumb Click Product Img Change js
// 08.Search Box Function
// 09.Add To Cart Notification js
// 10.Radio Parent Class js
// 11.SideBard Show Hide js
// 12.Blog Thumbs Active js
// 13.Select Dropdown Value Print js
// 14.Table Compare Remove Js
// 15.Tap To Top Js 
// 16.Input Number Length Validation Js 
// 17.Cookies js
// 18.Wishlist Remove js 
// 19.Cart Item Remove js
// 20.Pwa Service Worker Register
// افزودن event listener به فیلد جستجو




(function() {
    const selectors = {
        searchInput: '.search-type',
        suggestionList: '.search-suggestion ul',
        closeButton: '.close-search',
        loader: '.search-loader' // انتخابگر جدید برای لودر
    };

    // استایل لودر به صورت پویا اضافه می‌شود
    const addLoaderStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            .search-loader {
                display: none;
                position: relative;
                height: 60px;
                margin: 15px 0;
            }
            
            .loader-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    };

    function initSearch() {
        addLoaderStyles(); // افزودن استایل‌های لودر
        
        const searchInput = document.querySelector(selectors.searchInput);
        const suggestionList = document.querySelector(selectors.suggestionList);
        const closeButton = document.querySelector(selectors.closeButton);
        
        if (!searchInput || !suggestionList || !closeButton) return;

        // ایجاد عنصر لودر
        const loader = document.createElement('div');
        loader.className = 'search-loader';
        loader.innerHTML = '<div class="loader-spinner"></div>';
        suggestionList.parentNode.insertBefore(loader, suggestionList);

        let searchTimeout;
        let currentController; // برای مدیریت درخواست‌های لغو شده

        const toggleLoader = (show) => {
            loader.style.display = show ? 'block' : 'none';
        };

        const handleSearch = () => {
            const query = searchInput.value.trim();
            
            if (query.length >= 1) {
                toggleLoader(true); // نمایش لودر
                
                // لغو درخواست قبلی اگر وجود دارد
                if (currentController) {
                    currentController.abort();
                }
                
                const controller = new AbortController();
                currentController = controller;

                fetch(`/search/?q=${encodeURIComponent(query)}`, {
                    signal: controller.signal
                })
                .then(response => {
                    if (!response.ok) throw new Error('خطا در پاسخ سرور');
                    return response.json();
                })
                .then(data => {
                    toggleLoader(false); // مخفی کردن لودر
                    updateSuggestions(data.results);
                })
                .catch(error => {
                    if (error.name !== 'AbortError') {
                        toggleLoader(false);
                        console.error('Error:', error);
                    }
                });
            } else {
                toggleLoader(false);
                suggestionList.innerHTML = '';
            }
        };

        const updateSuggestions = (products) => {
            suggestionList.innerHTML = products.length
                ? products.map(product => {
                    let priceHTML;
                    
                    if (product.has_discount) {
                        priceHTML = `
                            <p class="mb-0 mt-1 text-danger">
                                ${product.discounted_price} تومان
                                <del class="text-muted ms-2">${product.original_price} تومان</del>
                            </p>
                        `;
                    } else {
                        priceHTML = `
                            <p class="mb-0 mt-1">${product.original_price} تومان</p>
                        `;
                    }
        
                    return `
                        <li>
                            <div class="product-cart media">
                                <img  src="${product.image}" class="img-fluid blur-up lazyload" alt="${product.title}">
                                <div class="media-body">
                                    <a href="${product.url}">
                                        <h6>${product.title}</h6>
                                    </a>
                                    <div class="price-container">
                                        ${priceHTML}
                                    </div>
                                    
                                </div>
                            </div>
                        </li>
                    `;
                }).join('')
                : '<li class="text-center">نتیجه‌ای یافت نشد</li>';
            
            feather.replace();
        };

        const debounce = (func, delay) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(func, delay);
        };

        searchInput.addEventListener('input', () => debounce(handleSearch, 300));
        closeButton.addEventListener('click', () => {
            searchInput.value = '';
            suggestionList.innerHTML = '';
            toggleLoader(false);
        });
    }

    document.addEventListener('DOMContentLoaded', initSearch);
})();






document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.view-product-btn');
        if (btn) {
            e.preventDefault();
            const slug = btn.dataset.slug;
            console.log('Clicked slug:', slug);

            // ارسال درخواست AJAX به ویو Django
            fetch(`/products/product-modal/${slug}/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(response => {
                    console.log('Status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Received data:', data);
                    const modal = document.getElementById('viewModal');

                    // به‌روز‌رسانی اسلایدر تصاویر (بندانگشتی و اصلی)
                    const thumbnailWrapper = modal.querySelector('.thumbnailSlider .swiper-wrapper');
                    const mainSliderWrapper = modal.querySelector('.mainslider .swiper-wrapper');
                    if (thumbnailWrapper && mainSliderWrapper && data.images && data.images.length > 0) {
                        let thumbnailHTML = '';
                        let mainSliderHTML = '';
                        data.images.forEach(function (imgSrc) {
                            thumbnailHTML += `
                <div class="swiper-slide">
                  <img src="${imgSrc}" alt="img" />
                </div>
              `;
                            mainSliderHTML += `
                <div class="swiper-slide">
                  <img class="bg-img" src="${imgSrc}" alt="img" />
                </div>
              `;
                        });
                        thumbnailWrapper.innerHTML = thumbnailHTML;
                        mainSliderWrapper.innerHTML = mainSliderHTML;
                        // (در صورت استفاده از Swiper، ری اینیشیالایز شود)
                    }

                    // به‌روز‌رسانی عنوان محصول
                    const titleElement = modal.querySelector('.product-option h4');
                    if (titleElement) {
                        titleElement.textContent = data.title;
                    }

                    // به‌روز‌رسانی قسمت قیمت
                    const priceContainer = modal.querySelector('.price-box');
                    if (priceContainer) {
                        const spanPrice = priceContainer.querySelector('span');
                        const delPrice = priceContainer.querySelector('del');
                        if (data.original_price) {
                            if (spanPrice) {
                                spanPrice.textContent = data.price + " تومان";
                            }
                            if (delPrice) {
                                delPrice.textContent = data.original_price + " تومان";
                                delPrice.style.display = 'inline';
                            }
                        } else {
                            if (spanPrice) {
                                spanPrice.textContent = data.price + " تومان";
                            }
                            if (delPrice) {
                                delPrice.style.display = 'none';
                            }
                        }
                    }

                    // به‌روز‌رسانی توضیحات محصول
                    const descriptionEl = modal.querySelector('.option .content-color');
                    if (descriptionEl) {
                        descriptionEl.innerHTML = data.description;
                    }

                    // به‌روز‌رسانی رنگ‌ها
                    const colorListEl = modal.querySelector('.filter-color');
                    if (colorListEl && data.colors && data.colors.length > 0) {
                        let colorsHTML = '';
                        data.colors.forEach(function (color, idx) {
                            colorsHTML += `
                            <li class="${idx === 0 ? 'active' : ''}">
                                <div class="color-box" style="background-color: ${color.code};"></div>
                            </li>
                            `;
                        });
                        colorListEl.innerHTML = colorsHTML;
                    } else if (colorListEl) {
                        colorListEl.innerHTML = '';
                    }
                    // بعد از درج رنگ‌ها به صورت داینامیک:
                    const colorItems = colorListEl.querySelectorAll('li');

                    colorItems.forEach(function (item) {
                        item.addEventListener('click', function () {
                            // حذف کلاس active از همه آیتم‌ها
                            colorItems.forEach(function (li) {
                                li.classList.remove('active');
                            });
                            // اضافه کردن کلاس active به آیتم کلیک شده
                            this.classList.add('active');
                        });
                    });

                    // به‌روز‌رسانی سایزها
                    const sizeListEl = modal.querySelector('.size-list');
                    if (sizeListEl && data.sizes && data.sizes.length > 0) {
                        let sizesHTML = '';
                        data.sizes.forEach(function (size, idx) {
                            sizesHTML += `<li ${idx === 0 ? 'class="active"' : ''}>${size}</li>`;
                        });
                        sizeListEl.innerHTML = sizesHTML;
                    } else if (sizeListEl) {
                        sizeListEl.innerHTML = '';
                    }
                    // به‌روز‌رسانی سایزها توسط جاوااسکریپت (رویداد کلیک)
                    if (sizeListEl && data.sizes && data.sizes.length > 0) {
                        let sizesHTML = '';
                        data.sizes.forEach(function (size, idx) {
                            sizesHTML += `<li ${idx === 0 ? 'class="active"' : ''}>${size}</li>`;
                        });
                        sizeListEl.innerHTML = sizesHTML;

                        // بعد از درج سایزها، افزودن رویداد کلیک برای تغییر کلاس active
                        const sizeItems = sizeListEl.querySelectorAll('li');
                        sizeItems.forEach(function (item) {
                            item.addEventListener('click', function () {
                                // حذف کلاس active از همه سایزها
                                sizeItems.forEach(function (li) {
                                    li.classList.remove("active");
                                });
                                // اضافه کردن کلاس active به آیتم کلیک شده
                                this.classList.add("active");
                            });
                        });
                    } else if (sizeListEl) {
                        sizeListEl.innerHTML = '';
                    }
                    // به‌روز‌رسانی لینک "مشاهده کامل" با استفاده از slug
                    const viewFullLink = modal.querySelector('.btn-outline');
                    if (viewFullLink) {
                        viewFullLink.setAttribute('href', '/products/' + data.slug );
                    }

                    // نمایش مودال با استفاده از Bootstrap Modal
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                })
                .catch(error => console.error('Error:', error));
        }
    });
});







"use strict";


// Body Selection //
const body = document.querySelector("body");

/*==================
  01. Loader js
======================*/
const loaderSpan = document.querySelector(".loader").children
const animate = function () {
    document.querySelector(".loader").classList.toggle('animate');
}
const timeOutAnimation = setInterval(animate, 1000);
document.onreadystatechange = function () {
    if (document.readyState !== "complete") {

        timeOutAnimation;
        body.classList.add("loader-overflow")
    } else {
        setTimeout(function () {
            document.querySelector(".loader-wrapper").classList.add("hidden")
            clearInterval(timeOutAnimation)
            body.classList.remove("loader-overflow")
        }, 1000)

    }
};

/*====================
   02. Ratio js
=======================*/
window.addEventListener('load', () => {
    const bgImg = document.querySelectorAll(".bg-img");
    for (i = 0; i < bgImg.length; i++) {

        let bgImgEl = bgImg[i];
        /// Optional Class Add /// 
        if (bgImgEl.classList.contains('bg-top')) {
            bgImgEl.parentNode.classList.add("b-top");
        }
        else if (bgImgEl.classList.contains('bg-bottom')) {
            bgImgEl.parentNode.classList.add("b-buttom");
        }
        else if (bgImgEl.classList.contains('bg-center')) {
            bgImgEl.parentNode.classList.add("b-center");
        }
        else if (bgImgEl.classList.contains('bg-left')) {
            bgImgEl.parentNode.classList.add("b-left");
        }
        else if (bgImgEl.classList.contains('bg-right')) {
            bgImgEl.parentNode.classList.add("b-right");
        }

        /// Lazyloader Class Add ///
        if (bgImgEl.classList.contains('blur-up')) {
            bgImgEl.parentNode.classList.add("blur-up", "lazyload");
        }

        /// Size Class Add ///
        if (bgImgEl.classList.contains('bg_size_content')) {
            bgImgEl.parentNode.classList.add("b_size_content");
        }

        /// Ratio Style ///
        bgImgEl.parentNode.classList.add("bg-size");
        const bgSrc = bgImgEl.src;
        bgImgEl.style.display = 'none';
        bgImgEl.parentNode.setAttribute("style", `
        background-image: url(${bgSrc});
        background-size:cover;
        background-position: center;
        background-repeat: no-repeat;
        display: block;
        `);
    }


    /*===============================
     Product Card After Image Set Js
     =====================================*/
    const productCard2 = document.querySelectorAll(".product-card2")
    productCard2?.forEach(el => {
        const primaryImg = el.querySelector(".primary-img").querySelector("img");
        const afterImg = el.querySelector(".after-img");
        afterImg.src = primaryImg.src
    })

});

/*===============================
  03. Language And Unit Select Js
=====================================*/
/// Language Select ///
const lang = document.querySelectorAll(".onhover-show-div .lang")
const languageSelected = document.querySelector("#languageSelected span")
for (var i = 0; i < lang.length; ++i) {
    lang[i].addEventListener('click', function () {
        languageSelected.innerHTML = this.innerHTML;
    })
}

/// Unit Select ///
const unit = document.querySelectorAll(".onhover-show-div .unit")
const unitSelected = document.querySelector("#unitSelected span")
for (var i = 0; i < unit.length; ++i) {
    unit[i].addEventListener('click', function () {
        unitSelected.innerHTML = this.innerHTML;
    })
}

/*=====================
   04. Cart Mobile js 
 ==========================*/
const cartButton = document.querySelector(".cart-button");
const cartBackButton = document.querySelector(".back-cart");
const showCard = document.querySelector(".shopingbag .onhover-show-div");
const overlay = document.querySelector(".overlay-general");
const overlayCart = document.querySelector(".overlay-cart");
if (window.matchMedia("(max-width: 768px)").matches) {
    cartButton?.addEventListener('click', function () {
        showCard.classList.add("show");
        overlayCart.classList.add("show");

    });
    const backCardSidemenu = function () {
        showCard.classList.remove("show");
        overlayCart.classList.remove("show");

    }
    cartBackButton?.addEventListener('click', backCardSidemenu)
    overlayCart?.addEventListener('click', backCardSidemenu)
}

/*=====================
 05. Plus Minus Item Js 
==========================*/
const plusMinus = document.querySelectorAll(".plus-minus ");
feather.replace();
for (var i = 0; i < plusMinus.length; ++i) {
    const addButton = plusMinus[i].querySelector(".add")
    const subButton = plusMinus[i].querySelector(".sub")
    addButton?.addEventListener('click', function () {
        const inputEl = this.parentNode.querySelector("input[type='number']");
        if (inputEl.value < 10) {
            inputEl.value = Number(inputEl.value) + 1;
        }
    })
    subButton?.addEventListener('click', function () {
        const inputEl = this.parentNode.querySelector("input[type='number']");
        if (inputEl.value >= 1) {
            inputEl.value = Number(inputEl.value) - 1;
        }
    })
};

/*=====================
 06. Footer Accordion Js 
==========================*/
const footerButton = document.querySelectorAll(".nav-footer h5");
const showNav = document.querySelector(".nav");
for (var i = 0; i < footerButton.length; ++i) {
    footerButton[i].addEventListener('click', function () {
        this.parentNode.classList.toggle('open');
    })
}

/*====================================
  0.7 Thumb Click Product Img Change js
 ========================================*/
const thumbEl = document.querySelectorAll(".product-card .thumbnail-img .thumb");
for (var i = 0; i < thumbEl.length; ++i) {
    thumbEl[i].addEventListener("click", function () {
        const parentEl = this.parentElement.children;
        [...parentEl].forEach((el) => {
            el.classList.remove("active");
        })
        this.classList.add("active");
        var imgSrc = this.querySelector("img").src;
        this.closest(".product-card").querySelector(".primary-img").style.backgroundImage = `url('${imgSrc}')`;
    });

};

/*=====================
 08. Search Box Function
 ==========================*/
const searchButton = document.querySelector(".search-button");
const searchFull = document.querySelector(".search-full");
searchButton?.addEventListener('click', function () {
    searchFull.classList.add("open");
});
window.addEventListener('load', () => {
    /// open search suggestion ///
    const searchType = document.querySelector(".search-type");
    searchType?.addEventListener('click', function () {
        this.parentNode.parentNode.classList.add("show");
    });

    /// close search  ///
    const closeSearch = document.querySelector(".close-search");
    closeSearch?.addEventListener('click', function () {
        const classes = ["open", "show"];
        classes.forEach(c => {
            if (searchFull.classList.contains(c)) {
                searchFull.classList.remove(c);
            }
        })
    });

});

/*================================
  09. Add To Cart Notification js
  ==================================*/
window.addEventListener('load', () => {
    const addToCartButton = document.querySelectorAll(".addtocart-btn ");
    addToCartButton.forEach((el) => {
        el.addEventListener("click", function () {
            document.querySelector(".addToCart").classList.add("show");
            setTimeout(() => { document.querySelector(".addToCart").classList.remove("show") }, 4000);
        })
    });
    const wishListButton = document.querySelectorAll(".wishlist-btn ");
    wishListButton.forEach((el) => {
        el.addEventListener("click", function () {
            document.querySelector(".addToWishlist").classList.add("show");
            setTimeout(() => { document.querySelector(".addToWishlist").classList.remove("show") }, 4000);
        })
    })

});


/*=====================
  10. Radio Parent Class js
 ==========================*/
const radio = document.querySelectorAll(".radio-input");
for (const radioEl of radio) {
    const parentAddressBox = document.querySelectorAll(".address-box");
    if (parentAddressBox.length !== 0) {
        radioEl?.addEventListener("change", function () {
            [...parentAddressBox].forEach((el) => {
                el.classList.remove("checked")
            })
            this.closest(".address-box")?.classList.add("checked")
        })
    }

}

/*=====================
  11. SideBard Show Hide js
  ==========================*/
/// Common Template ///
const sidebarToggle = function (showBtn, sidebar, overlay, backBtn) {
    showBtn?.addEventListener("click", function () {
        sidebar.classList.add("show-menu");
        overlay.classList.add("show");
        const removeFun = function () {
            sidebar.classList.remove("show-menu");
            overlay.classList.remove("show");

        }
        backBtn.addEventListener("click", removeFun)
        overlay.addEventListener("click", removeFun)
    });
}





/// User Dashboard SideBar ///
const settingMenuBtn = document.querySelector(".setting-menu");
const sideBarEl = document.querySelector(".side-bar");
const backBtnEl = document.querySelector(".back-side");
sidebarToggle(settingMenuBtn, sideBarEl, overlay, backBtnEl);

/// Shop Page SideBar ///
const filterOptionBtn = document.querySelector(".filter-btn");
const shopSideBar = document.querySelector(".sidebar-controll");
const backShopBtn = document.querySelector(".back-box");
sidebarToggle(filterOptionBtn, shopSideBar, overlay, backShopBtn);

/// Shop Top Filter Sidebar ///
const filterTopBtn = document.querySelector(".filter-top-btn");
const filterTopSidebar = document.querySelector(".filter-top-wrapper");
const filterTopBackBtn = document.querySelector(".filter-top-back");
sidebarToggle(filterTopBtn, filterTopSidebar, overlay, filterTopBackBtn);


/*=====================
  12. Blog Thumbs Active js
 ==========================*/
const actionBlogEl = document.querySelectorAll(".action-box .like-btn");
actionBlogEl.forEach(el => {
    el.addEventListener("click", function () {
        const parentEl = this.closest(".action-box").querySelectorAll(".like");
        parentEl.forEach(el => {
            el.classList.remove("active")
        })
        el.parentNode.classList.add("active");
    })
});


/*==================================
  13. Select Dropdown Value Print js
  =====================================*/
const selectList = document.querySelectorAll(".select-vallist");
selectList.forEach(function (el) {
    el.addEventListener("click", function (e) {
        e.preventDefault();
        const clicked = e.target.closest(".select-list")
        if (!clicked) return;
        const text = clicked.textContent
        const btnChangeText = this.closest(".dropdown").querySelector(".select-showval span");
        btnChangeText.textContent = text

    })
})


/*=========================
 14. Table Compare Remove Js 
=============================*/
const compareTable = document.querySelector(".table-compare")
compareTable?.addEventListener("click", function (e) {
    const clicked = e.target.closest(".remove")
    if (!clicked) return
    const th = [...clicked.closest("tr").children]
    const index = th.indexOf(clicked)
    const tableTd = clicked.closest(".table-compare").querySelectorAll("tbody tr ")

    tableTd.forEach(tr => {
        const td = tr.querySelectorAll("td")
        td[index].style.display = "none";
    })
    th[index].style.display = "none";
    return;
})



/*===================== 
15. Tap To Top Js 
==========================*/
const tapTopBtn = document.querySelector(".tap-to-top-button")
const tapTopTopBox = document.querySelector(".tap-to-top-box")
tapTopBtn?.addEventListener("click", function () {
    window.scroll({
        top: 0,
        behavior: 'smooth'
    });
})
if (tapTopTopBox) {
    window.onscroll = function () {
        if (pageYOffset >= 1000) {
            tapTopTopBox.classList.remove("hide")
        } else {
            tapTopTopBox.classList.add("hide")
        }
    }
}


/*===================================
16. Input Number Length Validation Js 
=======================================*/
function constrainUserInput() {
    const inputNumber = document.querySelectorAll("input[type='number']");
    inputNumber?.forEach(function (el) {
        el.addEventListener("keypress", function (e) {
            const maxLength = +el?.getAttribute("maxlength")
            if (maxLength) {
                const value = el.value
                if (value.length >= maxLength) {
                    el.value = value.substring(0, (el.maxLength - 1))
                }
            }
        })
    })
}
constrainUserInput();


/*===================
17. Cookies  js
=======================*/
const cookiesContainer = document.querySelector(".cookie-bar");
const cookiesAcceptBtn = document.querySelector(".cookies-accept")
window.addEventListener("load", function () {
    setTimeout(() => {
        cookiesContainer?.classList.add("show")
        if (cookiesContainer?.classList.contains("show")) {
            setTimeout(() => {
                cookiesContainer?.classList.remove("show")
            }, 10000);
        }
        cookiesAcceptBtn?.addEventListener("click", function () {
            cookiesContainer?.classList.remove("show")
        })
    }, 10000);

})


/*=====================
  18. Wishlist Remove js
  ==========================*/
const wishlistProduct = document.querySelectorAll(".product-wishlist")
wishlistProduct?.forEach(el => {
    const deleteButton = el.querySelector(".delete-button");
    deleteButton.addEventListener("click", function () {
        this.closest(".col").style.display = "none"
    })
})

/*=====================
  19. Cart Item Remove js
  ==========================*/
const cartBagProduct = document.querySelector(".shopingbag")
const cartRemoveBtn = cartBagProduct?.querySelectorAll(".remove-cart")
cartRemoveBtn?.forEach(el => {
    el.addEventListener("click", function () {
        this.closest(".cart-card").style.display = "none"
    })
})

/*=========================
  20.Pwa Service Worker Register
  ==============================*/
window.addEventListener("load", function () {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker
            .register('sw.js');
    }
})

