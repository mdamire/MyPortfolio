
const collapseSign = document.getElementById('collapse-sign');
const collapseButton = document.getElementById('collapse-button');

function addCollapseSign(){
    if (collapseButton && collapseButton.getAttribute('aria-expanded') === 'true') {
        collapseSign.textContent = '\u2796';
    } else if (collapseButton) {
        collapseSign.textContent = '\u2795';
    }
}

addCollapseSign()

if (collapseButton){
    collapseButton.addEventListener('click', function() {
        addCollapseSign()
    });
}

// Add this JavaScript to your script file
window.onscroll = function() {
    var button = document.getElementById("back-to-top");
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        button.style.display = "block";
    } else {
        button.style.display = "none";
    }
};

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
