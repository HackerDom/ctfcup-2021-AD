let rulesHeight = 0;
let ruleType = "group";
let groups = {};
let rules = [];


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


function genToken(callback) {
    $.ajax({
        url: "/gen_token",
        method: 'POST',
        processData: false,
    }).then(function (responseData) {
        callback(responseData);
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


function downloadResource() {
    let token = $("#token").val();
    let resourceUuid = $("#r-uuid").val();
    location.href = `/get_resource/${resourceUuid}?token=${token}`;
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

    $("#logout-btn").on('click', function (e) {
        logout();
    });

    bindLink("#to-res-btn", "/get_resource_page");
    bindLink("#to-reg-btn", "/register_page");
    bindLink("#to-log-btn", "/login_page");

    $("#add-token-btn").on('click', function (e) {
        addToken();
    });

    $("#get-res-btn").on("click", function (e) {
        downloadResource();
    });

    $("#rl-sel").on("change", function (e) {
        let v = $("#rl-sel").val();
        if (v === "action") {
            ruleType = v;
            $(".user-rule").hide();
            $(".group-rule").show();
        } else if (v === "group") {
            ruleType = v;
            $(".user-rule").show();
            $(".group-rule").hide();
        }
    });
    $("#add-rule-btn").on("click", addRule);
    $("#bnd-schema").on("click", function () {
        bindSchema(function (data) {
            uploadResource(data, function (uuid) {
                addResource(uuid);
                let schema = getSchema();
                setSchema(JSON.stringify(schema), uuid, function (data) {
                    resetChainRule();
                });
            });
        })
    });
}


function getRuleText() {
    let groupId = parseInt($("#grp-i").val());

    if (ruleType === "group") {
        let userId = parseInt($("#usr-i").val());
        if (userId < 1) {
            throw 'invalid user id (must be greater or equal than 1)';
        }
        if (!(userId in groups)) {
            groups[userId] = [];
        }
        groups[userId].push(groupId);
        return `user(${userId}) ∈ group(${groupId})`
    } else if (ruleType === "action") {
        let cond = $("#cond-sel").val();
        let action = $("#act-sel").val();
        rules.push([groupId, cond === "includes" ? 1 : 0, action === "allow" ? 1 : 0]);
        return `(user ∈ group(${groupId}) == ${cond}) → ${action}`;
    }
}


function getSchema() {
    let schema = {
        "groups": [[]],
        "rules": rules,
    };
    let maxUserId =  Math.max(...Object.keys(groups).map(x => parseInt(x)));
    for (let index = 1; index <= maxUserId; index++) {
        if (index in groups) {
            schema["groups"].push(groups[index]);
        } else {
            schema["groups"].push([]);
        }
    }
    return schema;
}


function addRule() {
    try {
        let ruleText = getRuleText();
        if (rulesHeight === tableHeight) {
            $("#tokens").append(`<tr><td id="t-0-${rulesHeight}"></td><td id="t-1-${rulesHeight}">${ruleText}</td><td id="t-2-${rulesHeight}"></td></tr>`);
            tableHeight++;
        } else {
            console.log(`#t-1-${rulesHeight}`);
            $(`#t-1-${rulesHeight}`).text(ruleText);
        }
        rulesHeight++;
    } catch (e) {
        alert(e);
    }
}


function addToken() {
    genToken(function (rawData) {
        let data = JSON.parse(rawData);
        if (tokensHeight === tableHeight) {
            $("#tokens").append(`<tr><td id="t-0-${tokensHeight}">${data["token"]} → ${data["count"]}</td><td id="t-1-${tokensHeight}"></td><td id="t-2-${tokensHeight}"></td></tr>`);
            tableHeight++;
        } else {
            $(`#t-0-${tokensHeight}`).text(`${data["token"]} -> ${data["count"]}`);
        }
        tokensHeight++;
    });
}


function addResource(uuid) {
    if (resourcesHeight === tableHeight) {
        $("#tokens").append(`<tr><td id="t-0-${resourcesHeight}"></td><td id="t-1-${resourcesHeight}"></td><td id="t-2-${resourcesHeight}">${uuid}</td></tr>`);
        tableHeight++;
    } else {
        $(`#t-2-${resourcesHeight}`).text(uuid);
    }
    resourcesHeight++;
}


async function readFile(file, callback) {
    await new Promise((resolve) => {
        let fileReader = new FileReader();
        fileReader.onload = (e) => resolve(fileReader.result);
        fileReader.readAsBinaryString(file);
    }).then(callback);
}


function uploadResource(data, callback) {
    $.ajax({
        url: "/upload_resource",
        method: 'POST',
        data: data,
        processData: false,
    }).then(function (responseData) {
        callback(responseData);
    })
        .catch(function (e) {
            alert(e.responseText);
        });
}


function setSchema(data, uuid, callback) {
    $.ajax({
        url: "/set_schema/" + uuid,
        method: 'POST',
        data: data,
        processData: false,
    }).then(function (responseData) {
        callback(responseData);
    })
        .catch(function (e) {
            alert(e.responseText);
        });
}


function resetChainRule() {
    for (let i = 0; i < rulesHeight; i++) {
        $(`#t-1-${i}`).text("");
    }
    $("#usr-i").text(1);
    $("#grp").text(1);
    rulesHeight = 0;
    tableHeight = Math.max(tokensHeight, resourcesHeight);
}


function bindSchema(callback) {
    let files = $("#file").prop("files");
    if (files.length === 0) {
        alert("Choose file!");
        return ;
    }

    let file = files[0];
    readFile(file, callback);
}


function main() {
    setHandlers();
}

$(document).ready(function () {
    main();
});