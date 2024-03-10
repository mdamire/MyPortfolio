
function getUrlParams(excludes){
    // Construct URL with parameters
    var existingParams = window.location.href.split('?')[1];
    var newParams = [];

    // Append existing query parameters to newParams
    if (existingParams) {
        var paramsArray = existingParams.split('&');
        paramsArray.forEach(function(param) {
            var paramName = param.split('=')[0];
            if (!excludes.includes(paramName)) {
                newParams.push(param);
            }
        });
    }

    return newParams
}


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

    var newParams = getUrlParams(['tags', 'sort']);

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
    var newParams = getUrlParams(['page']);
    newParams.push('page=' + pageNumber);
    let url = window.location.pathname + '?' + newParams.join('&');

    window.location.href = url;
}


function clearFilters(){
    var remainingParams = getUrlParams(['tags', 'sort']);
    let url = window.location.pathname 
    if (remainingParams.length > 0) {
        url = url + '?' + remainingParams.join('&');
    }

    window.location.href = url
}
