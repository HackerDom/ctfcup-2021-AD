function removeAllCookies() {
    const cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
}


function logout() {
    removeAllCookies();
    location.href = "/login_page";
}


function auth(method, data) {
    $.ajax({
        url: method,
        method: 'POST',
        data: data,
        processData: false,
    }).then(function (responseData) {
        console.log(responseData);
        location.href = "/"
    })
        .catch(function (e) {
            alert(e.responseText);
        });
}


function bindLink(selector, url) {
    $(selector).on('click', function () {
        location.href = url;
    });
}


function setHandlers() {
    [
        ["#reg-btn", "/register"],
        ["#log-btn", "/login"],
    ].forEach(function (pair) {
        $(pair[0]).on('click', function (e) {
            let username = $("#login").val()
            let password = $("#password").val()
            auth(pair[1], JSON.stringify({
                "name": username,
                "password": password,
            }));
        });
    });

    //
    // $("#logout-btn").on('click', function (e) {
    //     logout();
    // });
    //
    // $("#ane-btn").on('click', function (e) {
    //     createEmployee();
    // });

    bindLink("#to-reg-btn", "/register_page");
    bindLink("#to-log-btn", "/login_page");
    // bindLink("#to-home-btn", "/");
    // bindLink("#to-new-empl-btn", "/add_employee_page");
}


function main() {
    setHandlers();
}

$(document).ready(function () {
    main();
});