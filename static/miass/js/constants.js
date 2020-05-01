/**
 * Created by hanter on 2016. 4. 14..
 */

var SERVER_ADDRESS = 'http://localhost:8000';
//var SERVER_ADDRESS = 'http://203.253.21.226:8000';

var POSSIBLE_MULTIPLE_IMAGE_UPLOAD_NUM = 300;


// function set_current_user(c_u) {
//     // sessionStorage.setItem("current_user", JSON.stringify(c_u));
//     localStorage.setItem("current_user", JSON.stringify(c_u));
// }
// function get_current_user() {
//     // return JSON.parse(sessionStorage.getItem("current_user"));
//     return JSON.parse(localStorage.getItem("current_user"));
// }
//
// function remove_current_user() {
//     // sessionStorage.clear();
//     localStorage.clear();
//     // sessionStorage.removeItem("current_user");
//     localStorage.removeItem("current_user");
// }
//
// function set_current_page(c_p) {
//     localStorage.setItem("current_page", c_p);
//     // sessionStorage.setItem("current_page", c_p);
// }
//
// function get_current_page() {
//     // if (sessionStorage.getItem("current_page")===undefined || sessionStorage.getItem("current_page")===null){
//     //     return 0;
//     // }else{
//     //     return sessionStorage.getItem("current_page");
//     // }
//     if (localStorage.getItem("current_page")===undefined || localStorage.getItem("current_page")===null){
//         return null;
//     }else{
//         return localStorage.getItem("current_page");
//     }
// }
//
// function remove_current_page() {
//     // sessionStorage.removeItem("current_page");
//     localStorage.removeItem("current_page");
// }
//
// function clear_session() {
//     // sessionStorage.clear();
//     localStorage.clear();
// }
//
// function is_refreshed(i) {
//     localStorage.setItem("is_refresh",i);
// }
//
// function get_is_refreshed() {
//     return localStorage.getItem('is_refresh');
// }
//
// function set_login_time(i) {
//     localStorage.setItem("login_timestamp", i);
// }
//
// function get_login_time() {
//     return localStorage.getItem("login_timestamp");
// }