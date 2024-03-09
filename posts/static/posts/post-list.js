
function submitFilters(){
    let checkedItems = [];
    let filterSettings = document.getElementById('filter-settings');

    // Get checked items from the checkbox list
    var checkboxes = filterSettings.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach(function(checkbox) {
        checkedItems.push(checkbox.value);
    });

    // Get the selected value from the radio button
    var selectedOption = filterSettings.querySelector('input[type="radio"]:checked');
    var optionValue = selectedOption ? selectedOption.value : '';

    // Construct URL with parameters
    var currentUrl = window.location.href;
    var existingParams = currentUrl.split('?')[1]; // Get the existing query parameters
    var newParams = [];

    // Append existing query parameters to newParams
    if (existingParams) {
        var paramsArray = existingParams.split('&');
        paramsArray.forEach(function(param) {
            var paramName = param.split('=')[0];
            if (paramName !== 'tags' && paramName !== 'sort') {
                newParams.push(param);
            }
        });
    }

    // Append new query parameters
    if (checkedItems.length > 0) {
        newParams.push('tags=' + checkedItems.join(','));
    }
    if (optionValue !== '') {
        newParams.push('sort=' + optionValue);
    }

    var url = window.location.pathname;
    // Combine the base URL and new query parameters
    if (newParams.length > 0) {
        url += '?' + newParams.join('&');
    }

    // Reload page with the new URL
    window.location.href = url;
}


function changePage(pageNumber){
    // Construct URL with parameters
    var currentUrl = window.location.href;
    var existingParams = currentUrl.split('?')[1]; // Get the existing query parameters
    var newParams = [];

    // Append existing query parameters to newParams
    if (existingParams) {
        var paramsArray = existingParams.split('&');
        paramsArray.forEach(function(param) {
            var paramName = param.split('=')[0];
            if (paramName !== 'page') {
                newParams.push(param);
            }
        });
    }
    
    newParams.push('page=' + pageNumber);

    let url = window.location.pathname + '?' + newParams.join('&');

    window.location.href = url;
}
