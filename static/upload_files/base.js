$(function () {
/* 1. OPEN THE FILE EXPLORER WINDOW */
    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

  /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
    $("#fileupload").fileupload({  //fileupload
        dataType: 'json',
        done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER  这里的data来自于JsonResponse传来的data*/
              if (data.result.is_valid) {
                  $("#gallery tbody").prepend(
                      "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
                  )
            }
        }
    });
});