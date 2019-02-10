"use strict"
$(".brighten").click(function() {
  window.location = $(this).find("a").attr("href");
  return false;
});

$(".demo-card-wide").hover(
    function() {
        $(this).toggleClass('mdl-shadow--8dp').toggleClass('mdl-shadow--2dp');

    }
);
let hide = {
    loginbutton: function(){
      $('.signInButtonTitle').hide();
      $('.signOutButtonTitle').show();
      $('.signInButton').hide();
      $('#user_info').show();
      $('#logout_button1').show();
    },
    userinfo: function(){
      $('#user_info').hide();
      $('.signInButtonTitle').show();
      $('.signOutButtonTitle').hide();
      $('.signInButton').show();
      $('#logout_button1').hide();
    }
}

if((logged === 'null')||(logged === '')){
  hide.userinfo();
}
else{
  hide.loginbutton();
}

let notification = document.querySelector('.mdl-js-snackbar');

let validateDetails = function() {
  let albumTitle = $('#albumTitle');
  let artist = $('#artist');
  let coverartUrl = $('#coverarturl');
  let description = $('#description');
  let genre = $('#genre');

  if (albumTitle.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Album Title Can't be Empty!"
      }
    );
    albumTitle.focus();
    return false;
  }
  else if (artist.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Artist also required :)"
      }
    );
    artist.focus();
    return false;
  }
  else if (coverartUrl.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Coverart Image Url also Required!"
      }
    );
    coverartUrl.focus();
    return false;
  }
  else if (description.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Please provide some description of album!"
      }
    );
    description.focus();
    return false;
  }
  else if (genre.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Please Select Album Genre!"
      }
    );
    return false;
  }

  $('#albumForm').submit();

};

let googleSignInCallback = function(authResult){
    if (authResult['code']){
        $.ajax({
            type: 'POST',
            url: '/gconnect?state=' + state,
            processData: false,
            contentType: 'application/json',
            data: authResult['code'],
            success: function(result){
                if(result){
                    var img = result['img'].replace('https','http');
                    hide.loginbutton();
                    $('#userImg').attr('src',img);
                    $('#userName').html(result['name']);
                    $('#userEmail').html(result['email']);
                    logged = 'google';
                }
                else if (authResult['error']){
                    console.log("Following Error Occured:" + authResult['error']);
                }
                else{
                    console.log('Failed to make connection with server, Please check your internet connection.');
                }
            }
        });
    }
};


let logout = function(){

   if(logged=='google'){

    $.ajax({

      type: 'POST',
      url: '/logout',
      processData: false,
      contentType: 'application/json',
      success: function(result){
        if(result['state'] == 'loggedOut'){
          console.log(window.location.href + "?error=" + "successLogout");
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "You have been Successfully Logged out!"
            }
          );
          hide.userinfo();

        }
        else if (result['state'] == 'notConnected'){
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "User not Logged in!"
            }
          );
        }
        else if (result['state'] == 'errorRevoke'){
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "Error Revoking User Token!"
            }
          );
        }

      }

    });

   }
   else{

     notification.MaterialSnackbar.showSnackbar(
       {
         message: "User not Logged in!"
       }
     );
   }

}

gapi.signin.render("googleSignIn", {
              'clientid': '277210399189-1ejbfqb4mdt07ektbe3bnj3va2nnf051.apps.googleusercontent.com',
              'callback': googleSignInCallback,
              'cookiepolicy': 'single_host_origin',
              'requestvisibleactions': 'http://schemas.google.com/AddActivity',
              'scope': 'openid email',
              'redirecturi': 'postmessage',
              'accesstype': 'offline',
              'approvalprompt': 'force'
});

gapi.signin.render("googleSignInCustom", {
              'clientid': '277210399189-1ejbfqb4mdt07ektbe3bnj3va2nnf051.apps.googleusercontent.com',
              'callback': googleSignInCallback,
              'cookiepolicy': 'single_host_origin',
              'requestvisibleactions': 'http://schemas.google.com/AddActivity',
              'scope': 'openid email',
              'redirecturi': 'postmessage',
              'accesstype': 'offline',
              'approvalprompt': 'force'
});

$('#logout_button').click(function(){
    logout();
});

$('#logout_button1').click(function() {
  logout();
});
