
const collapseSign = document.getElementById('collapse-sign');
const collapseButton = document.getElementById('collapse-button');

function addCollapseSign(){
    if (collapseButton.getAttribute('aria-expanded') === 'true') {
        collapseSign.textContent = '\u2796';
    } else {
        collapseSign.textContent = '\u2795';
    }
}

addCollapseSign()

collapseButton.addEventListener('click', function() {
    addCollapseSign()
});
