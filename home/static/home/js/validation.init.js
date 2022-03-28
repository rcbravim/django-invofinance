!function(){'use strict';window.addEventListener('load',function(){var t=document.getElementsByClassName('needs-validation');Array.prototype.filter.call(t,function(e){e.addEventListener('submit',function(t){errorVerifier();!1===e.checkValidity()&&(t.preventDefault(),t.stopPropagation()),e.classList.add('was-validated')},!1)})},!1)}();

function errorVerifier() {
    var email = $('.valid_email').val();
    if (email) { if (!validEmail(email)) { $('.valid_email').nextAll('div:first').text('Email provided is invalid'); $('.valid_email').val(''); }}

    var pass = $('.valid_pass').val();
    if (pass) {
        var bypass = false;
        if ($('.valid_pass').hasClass('bypass')) { bypass = true; }
        var valid = validPassword(pass, bypass);
        if (valid.length > 0) {
            if (valid.includes('special')) { $('.valid_pass').nextAll('div:first').text('Password cannot contain disallowed characters. e.g. ";"'); }
            else if (valid.includes('number')) { $('.valid_pass').nextAll('div:first').text('Password must contain at least ONE number in its composition'); }
            else if (valid.includes('upper')) { $('.valid_pass').nextAll('div:first').text('Password must contain at least ONE capital letter in its composition'); }
            else if (valid.includes('lower')) { $('.valid_pass').nextAll('div:first').text('Password must contain at least ONE lowercase letter in its composition'); }
            $('.valid_pass').val('');
        } else if (pass.length < 8) { $('.valid_pass').nextAll('div:first').text('Password must contain at least 8 characters'); $('.valid_pass').val(''); }
    }

    var pass_confirm = $('.valid_pass_confirm').val();
    if (pass_confirm) { if (pass_confirm != pass) { $('.valid_pass_confirm').nextAll('div:first').text('The password and its confirmation are not the same'); $('.valid_pass_confirm').val(''); }}
}


//------------------------------------------------------------------------------------------//
//------------------------------VALIDATION/HELPER FUNCTIONS---------------------------------//
//------------------------------------------------------------------------------------------//


// EMAIL VALIDATION
function validEmail(email){var re=/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;return re.test(email);}

// PASSWORD VALIDATION
function validPassword(pass, bypass){var special = /^[a-zA-Z0-9-!@#$%^&*()_+\-=\[\]{}\\|,.<>\/?~]*$/;var number=/[0-9]/;var upper=/[A-Z]/;var lower=/[a-z]/;var error=[];if(!special.test(pass)){error.push('special');}if(!number.test(pass)&&!bypass){error.push('number');}if(!upper.test(pass)&&!bypass){error.push('upper');}if(!lower.test(pass)&&!bypass){error.push('lower');}return error;}