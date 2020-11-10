"use strict"

function update_5_min() {
    console.log('update_5_min')
    let request = new XMLHttpRequest()

    request.onreadystatechange = function() {
        if (request.readyState != 4) return
    }

    request.open("GET", "", true)
    request.send()
}

function update_1_day() {
    console.log('update_1_day')
    let request = new XMLHttpRequest()

    request.onreadystatechange = function() {
        if (request.readyState != 4) return
    }

    request.open("GET", "daily_session", true)
    request.send()
}
