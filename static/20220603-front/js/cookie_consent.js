var cookie_btn = document.getElementById('ok_cookie_box');
if(cookie_btn){
    cookie_btn.addEventListener('click', function () {

        document.cookie = "CookieConsent=1;domain="+domain_name;

        document.getElementById("cookie_consent_popup").style.display = "none";
    })
}