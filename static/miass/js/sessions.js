function set_current_user(c_u) {
    // sessionStorage.setItem("current_user", JSON.stringify(c_u));
    sessionStorage.setItem("current_user", JSON.stringify(c_u));
    var c_r = c_u['role'].split(' ')[0];
    sessionStorage.setItem("current_role", JSON.stringify(c_r));
}

function get_current_user() {
    // return JSON.parse(sessionStorage.getItem("current_user"));
    return JSON.parse(sessionStorage.getItem("current_user"));
}

function set_current_role(role) {
    sessionStorage.setItem("current_role", JSON.stringify(role));
}

function get_current_role() {
    return JSON.parse(sessionStorage.getItem("current_role"));
}

function remove_current_user() {
    sessionStorage.clear();
    sessionStorage.removeItem("current_user");
    sessionStorage.removeItem("current_role");
}

function clear_session() {
    sessionStorage.clear();
}

function set_remember(c_u){
    localStorage.setItem("saved_user", JSON.stringify(c_u));
}

function get_remember() {
    return JSON.parse(localStorage.getItem("saved_user"));
}

function remove_remember() {
    localStorage.removeItem("saved_user");
    localStorage.clear();

}