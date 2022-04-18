 var name="Deepika Bisht"
 window["iframes_count"]=0

/*
const progressBar = `
   <div class="momane_overlay"></div>
   <div class="momane_progressBar">
     <div class="momane_finished">
     <img src="${chrome.extension.getURL("images/header.png")}"  style="height:130px"/ >
   </div>
   <div class="momane_text">Automatication is going on. Please wait ......</div>
     <div class="momane_progressInfo">
       <span class="momane_done">0</span> of <span class="momane_sum">100</span>
     </div>
     <button class="momane_stop">Stop</button>
   </div>
 `;

var ausers=[];
var Ttarget_id='';

 jQuery(document).on("click","button[name='approve_all']",function(e){

$("div._3k4n ul.uiList li").each(function () {
  var uu=$(this).find("a[uid]").attr("uid")
 if(uu)
 ausers.push($(this).find("a[uid]").attr("uid"))
})
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
                  var tg=target_id.target_id.post_id
                  tg=tg.replace("gm.",'')
                  tg=tg.trim()
                   Ttarget_id=tg
                   $("body").append(progressBar);
                   $(".momane_sum").text(ausers.length);
                   $(".momane_done").text('1');

                 for(i=0;i<ausers.length;i++){

                   (function(i) {
        setTimeout(function() {
          console.log(i);
          var uuid=ausers[i]
          var uri='https://d.facebook.com/mbasic/comment/advanced/?target_id='+tg+'&pap&at=compose&photo_comment&ids='+uuid+'&is_from_friend_selector=1&_rdr';
           console.log(uri)
         AppendIframe(uri);
         $(".momane_done").text(i+1);

        }, 1000 * i);
    })(i);

                 }



                })


            }else{

            }
          }else{

          }
        }
      });
    }
  });

});

*/

 jQuery(document).on("click","button[name='approve']",function(e){
   var uuid=$(this).parent().next().find('a').attr("uid")
    //alert("UUID"+uuid)
    console.log(uuid)
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
                   var tg=target_id.target_id.post_id
                   tg=tg.replace("gm.",'')
                   tg=tg.trim()
                   var uri='https://d.facebook.com/mbasic/comment/advanced/?target_id='+tg+'&pap&at=compose&photo_comment&ids='+uuid+'&is_from_friend_selector=1&frame_id=68716';
                   console.log(uri)
                   chrome.runtime.sendMessage({url: uri})
                 })


             }else{

             }
           }else{

           }
         }
       });
     }
   });

 })

 var iframe=''
 function AppendIframe(url, type) {
   Kill_Iframes()
   window["iframes_count"]++;
   var frameID = 68716;
   iframe = document.createElement('iframe');
   iframe.setAttribute('id', 'Frame-' + frameID);
   iframe.setAttribute('class', 'iframeObject');
   iframe.setAttribute('style', 'height:0;opacity:0');
   iframe.src = url;
   document.body.appendChild(iframe);
 }

 function Kill_Iframes() {
   var iframes = document.querySelectorAll('.iframeObject');
   for (var i = 0; i < iframes.length; i++) {
     iframes[i].parentNode.removeChild(iframes[i]);
   }
 }
