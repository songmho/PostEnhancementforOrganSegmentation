function set_current_user(c_u) {
    // sessionStorage.setItem("current_user", JSON.stringify(c_u));
    sessionStorage.setItem("current_user", JSON.stringify(c_u));
}

function get_current_user() {
    // return JSON.parse(sessionStorage.getItem("current_user"));
    console.log(sessionStorage.getItem("current_user"));
    console.log(localStorage.getItem("saved_user"));
    return JSON.parse(sessionStorage.getItem("current_user"));
}

function remove_current_user() {
    // sessionStorage.clear();
    sessionStorage.clear();
    // sessionStorage.removeItem("current_user");
    sessionStorage.removeItem("current_user");
}

function clear_session() {
    // sessionStorage.clear();
    sessionStorage.clear();
}

function set_remember(c_u){
    localStorage.setItem("saved_user", JSON.stringify(c_u));
}

function get_remember() {
    console.log(localStorage.getItem("saved_user"));
    return JSON.parse(localStorage.getItem("saved_user"));
    return localStorage.getItem("saved_user");
}

function remove_remember() {
    localStorage.removeItem("saved_user");
    localStorage.clear();

}