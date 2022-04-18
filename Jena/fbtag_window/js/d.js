var DONE=0;
Array.prototype.sample = function(){
  return this[Math.floor(Math.random()*this.length)];
}
window.onload=function(){
  setTimeout(function(){
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const product = urlParams.get('frame_id')
    if(product=='68716' && DONE==0){
      chrome.storage.local.get("target_id", function(target_id) {

        var messges=[]
        var msg=''
        jQuery.each(target_id.target_id,function(k,v){
          if(k!='post_id')
          messges.push(v)
        })
        if(messges){
          msg=messges.sample()
        }else{
          msg='Hey welcome here!'
        }
        jQuery("textarea[name='comment_text']").val(msg)
        setTimeout(function(){
          jQuery("input[name='post']").click();
          setTimeout(function(){
              chrome.runtime.sendMessage({closeThis: true})
          },1000)
        },1000)
        DONE==1
      })
    }else{

    }
  },500)


}
