function set_current_profile(d){
    sessionStorage.removeItem("profile");
    // console.log(d);
    sessionStorage.setItem("profile", JSON.stringify(d));
}
function get_current_profile() {
    // console.log(JSON.parse(sessionStorage.getItem("profile")));
    return JSON.parse(sessionStorage.getItem("profile"));
}
function remove_current_profile() {
    var voice = get_voice();
    sessionStorage.removeItem("profile");
    set_voice(voice);
}
function set_current_user(c_u) {
    // sessionStorage.setItem("current_user", JSON.stringify(c_u));
    sessionStorage.setItem("current_user", JSON.stringify(c_u));
    console.log(c_u);
    try{
        var c_r = c_u['role'].split(' ')[0];
    } catch (e) {
        var c_r = c_u['role'];
    }

    sessionStorage.setItem("current_role", JSON.stringify(c_r));
}

function get_current_user() {
    // return JSON.parse(sessionStorage.getItem("current_user"));
    return JSON.parse(sessionStorage.getItem("current_user"));
}

function set_current_role(role) {
    sessionStorage.setItem("current_role", JSON.stringify(role));
    $.ajax({
        url: "/api/change_role_order",
        method: 'POST',
        async: true,
        data: JSON.stringify({
            "id": get_current_user()["identification_number"],
            "role": role,
        }),
        success: function (data) {
            console.log(data);
            if (data["state"]){

            }else{

            }
        }, error: function (err) {
            console.log(err);
        }
    });
}

function get_current_role() {
    return JSON.parse(sessionStorage.getItem("current_role"));
}

function remove_current_user() {
    var voice = get_voice();
    sessionStorage.clear();
    sessionStorage.removeItem("current_user");
    sessionStorage.removeItem("profile");
    sessionStorage.removeItem("current_role");
    set_voice(voice);
}

function clear_session() {
    var voice = get_voice();
    sessionStorage.clear();
    set_voice(voice);
}

function set_remember(c_u){
    localStorage.setItem("saved_user", JSON.stringify(c_u));
}

function get_remember() {
    return JSON.parse(localStorage.getItem("saved_user"));
}

function remove_remember() {
    var voice = get_voice();
    localStorage.removeItem("saved_user");
    localStorage.clear();
    set_voice(voice);

}

function set_voice(d){
    localStorage.setItem("voice", JSON.stringify(d));
}
function get_voice() {
    return JSON.parse(localStorage.getItem("voice"));
}