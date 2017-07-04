$(document).ready(function() {
    $('#coord-form').hide()
    $('#weather table').hide()
    $('#weather-0').addClass('active-tab')
    $('#table-0').show()

    document.querySelector('#city-input').addEventListener('input', function() {
        var xhr = new XMLHttpRequest()
        xhr.open('GET', '/find?q=' + this.value)
        xhr.onload = function() {
            var findData = JSON.parse(xhr.responseText)
            var result = ''
            for (var city of findData.list) {
                result += '<li><a href="/?id=' + city.id + '" class="search-tip"><span>' + city.name + '</span> <span>' + city.sys.country + '</span></a></li>'
            }
            document.querySelector('#search-tips').innerHTML = result
        }
        xhr.send()
    })
    $('body').on('click', '.flex-block', function() {
        $('.flex-block').removeClass('active-tab')
        var num = Number(this.id.substr(-1))
        $('#weather-' + num).addClass('active-tab')
        $('#weather table').hide()
        $('#table-' + num).show()
    })

    $('#caret-down').click(function(e) {
        e.preventDefault()
        $('#search-form').hide()
        $('#coord-form').show()
    })
    $('#caret-up').click(function(e) {
        e.preventDefault()
        $('#coord-form').hide()
        $('#search-form').show()
    })
})
