"use strict"

function update_5_min() {
    console.log('1')
    let request = new XMLHttpRequest()

    request.onreadystatechange = function() {
        if (request.readyState != 4) return
    }

    request.open("GET", "", true)
    request.send()
}

function update_1_day() {
    console.log('2')
    let request = new XMLHttpRequest()

    request.onreadystatechange = function() {
        if (request.readyState != 4) return
    }

    request.open("GET", "daily_session", true)
    request.send()
}
