(function () {

    //CONFIGURATION
    var headerClassName = 'header-common'; //Class of your header element
    var stickyAfter = 150; //Show fixed header after this Y offset in px
    var header = document.getElementsByClassName(headerClassName)[0];
    // var clone = header.cloneNode(true);
    header.classList.add('clone');
    // header.parentElement.appendChild(clone);
    const header4LogoChange = document.querySelector('.header4LogoChange');

    var initializeHeader = function () {
        document
            .getElementsByClassName(headerClassName + ' clone')[0]
            .classList.add('initialized');
        return true;
    }
    window.onscroll = function () {
        var cl = document.body.classList;
        if (window.pageYOffset > stickyAfter) {
            initializeHeader()
            cl.add('sticky');

        } else {
            cl.remove('sticky');

        }
        if (!header4LogoChange) return
        if (header4LogoChange?.classList.contains("clone")) {
            const html = document.querySelector('html');
            const logo = header4LogoChange.querySelector(".logo");
            const logoSrc = logo.getAttribute("src");
            const logoWhite = "../assets/images/logos/logo-4-w.png"
            if (cl.contains("sticky") && html.classList.contains("dark") && logoSrc !== logoWhite) {
                logo.setAttribute("src", logoWhite);
            } else if (!cl.contains("sticky")) {
                logo.setAttribute("src", "../assets/images/logos/logo-4.png")
            }

        }
    }

})();