
var grid = document.querySelector('.grid');
var msnry;
// element selectors
var imgAll = document.querySelectorAll('.grid-item');
var imgFashion = document.querySelectorAll('.fashion');
var imgBags = document.querySelectorAll('.bags');
var imgOthers = document.querySelectorAll('.others');
// buttons
const tabsUl = document.getElementById('filter-btn-group');
const lis = tabsUl.children;
const gridItems = grid.children;


imagesLoaded(grid, function () {
    setTimeout(() => {
        msnry = new Masonry(grid, {
            //options
            itemSelector: '.grid-item',
            columnWidth: '.grid-sizer',
            percentPosition: true,
            isOriginLeft: false
        });
    }, 1000)
});




//element & class name
function toggleClass(childElems, parentElem, className) {

    [...parentElem].map(element => {
        const elementBtn = element.querySelector(".btn-filter");
        elementBtn?.classList.remove(className)

    });
    childElems.classList.add(className)

}

function showImages(showImg, hideImg1, hideImg2) {
    for (let i = 0; i < showImg.length; i++) {
        showImg[i].style.display = "block";
    }
    for (let i = 0; i < hideImg1.length; i++) {
        hideImg1[i].style.display = "none";
    }
    for (let i = 0; i < hideImg2.length; i++) {
        hideImg2[i].style.display = "none";
    }
}


tabsUl.addEventListener('click', (event) => {
    let tabLi = event.target.closest(".btn-filter");
    if (!tabLi) return
    toggleClass(tabLi, lis, 'active');

    //show all images
    if (event.target.id == "all") {
        for (let i = 0; i < imgAll.length; i++) {
            imgAll[i].style.display = "block";
        }
    }

    //show ny images 
    if (event.target.id == "fashion") {
        showImages(imgFashion, imgBags, imgOthers);
    }

    // show flowers
    if (event.target.id == "bags") {
        showImages(imgBags, imgFashion, imgOthers);
    }

    // show other images
    if (event.target.id == "others") {
        showImages(imgOthers, imgBags, imgFashion);
    }

    msnry.layout();

});



