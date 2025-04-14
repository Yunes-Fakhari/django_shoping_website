document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.select-list a').forEach(function(element) {
        element.addEventListener('click', function(event) {
            event.preventDefault();
            var sortValue = this.getAttribute('href').split('=')[1];
            document.getElementById('sortInput').value = sortValue;
            document.getElementById('sortForm').submit();
        });
    });
});
