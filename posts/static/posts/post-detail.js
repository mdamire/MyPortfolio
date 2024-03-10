
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
