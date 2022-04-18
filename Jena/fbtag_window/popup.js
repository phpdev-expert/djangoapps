
checklogin();
var URL='http://18.191.249.158/public/api'
function checklogin(){
  $("#loader").show();

  chrome.storage.local.get("login", function(items) {
    if (!chrome.runtime.error){
      chrome.storage.local.get("logintime", function(logtime) {
        if (!chrome.runtime.error) {
          var prevdt=logtime.logintime
          var millis = Date.now() - prevdt;
          var tots= Math.floor(millis/1000)
          if(items.login){
            if(items.login.status==1 && tots < 86400){
                chrome.storage.local.get("target_id", function(target_id) {
                  $.each(target_id.target_id,function(k,v){
                    $("input[name='"+k+"']").val(v)
                  })
                })

              $("#loader").hide();
              $("#dashboard").show();
            }else{
              $("#loader").hide();
              $("#form_container").show();
            }
          }else{
            $("#loader").hide();
            $("#form_container").show();
          }
        }
      });
    }
  });
}

$("#forgotpasslink").click(function(){

  $("#form_container").hide();
  $("#forgotpass").show();
})

$("#loginBackBtn").click(function(){
  $("#form_container").show();
  $("#forgotpass").hide();
})

$("#btn_logout").click(function(){

  $("#form_container").show();
  $("#dashboard").hide();
  var resp={status:0};
  chrome.storage.local.set({ "login" : resp }, function() {
          if (chrome.runtime.error) {
            console.log("Runtime error.");
          }
        });

})


$("#btn_save_data").click(function(){
  var resp={};
  $(".uinput").each(function(){
     resp[$(this).attr('name')]=$(this).val()
  })

  chrome.storage.local.set({"target_id" : resp }, function() {
          if (chrome.runtime.error) {
            console.log("Runtime error.");
          }

          $("#succse_msg").show();
          setTimeout(function(){
            $("#succse_msg").hide()
          },1000)

        });

})




$("#dologin").click(function(){
  $("#loader").show();
  //alert($("#username").val());
  $.ajax({
    url:URL+'/users',
    data:{email:$("#username").val(),password:$("#password").val()},
    type:'post',
    success:function(data){

      $("#loader").hide();

	  var resp=data;
    // alert(data)
	  if(resp.status==1){
        chrome.storage.local.set({ "login" : resp }, function() {
          if (chrome.runtime.error) {
            console.log("Runtime error.");
          }
        });
        var now = Date.now()
        chrome.storage.local.set({ "logintime" : now  }, function() {
          if (chrome.runtime.error) {
            console.log("Runtime error.");
          }
        });

        $("#form_container").hide();
        $("#dashboard").show();
      }else{
        $("#error").show();
        $("#text-msg").text('Invalid login details')
      }

    }
  })

  return false;
})

$("#supprot_btn").click(function(){
chrome.tabs.create({ url: 'https://www.hellohostess.co/support'});
})

$("#new_account").click(function(){
  chrome.tabs.create({ url: 'https://www.hellohostess.co'});
})
$("#forget_pass_tab").click(function(){
  chrome.tabs.create({ url: 'http://18.191.249.158/public/password/reset'});
})




$("#affliate_btn").click(function(){
  chrome.tabs.create({ url: 'https://www.hellohostess.co/affiliate-tools'});

})
