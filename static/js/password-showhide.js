

/*==============================
   Password Showhide js
 =====================================*/
const showHideBtn = document.querySelectorAll(".showHidePassword");
let activeEye = 1;
for (let i = 0; i < showHideBtn.length; ++i) {
    showHideBtn[i].addEventListener("click", function () {
        let inputEl = showHideBtn[i].parentNode.querySelector("input");
        if (inputEl.type === "password") {
            inputEl.type = "text"
            activeEye = 2
        } else {
            inputEl.type = "password"
            activeEye = 1
        }
        showHideBtn[i].src = `../static/icons/svg/eye-${activeEye}.svg`;
    });
}

