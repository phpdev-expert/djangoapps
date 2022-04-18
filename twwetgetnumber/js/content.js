var interv
var xc = [];
var scrollingElement = (document.scrollingElement || document.body)


window.onload = function(e) {

 interv = setInterval(function() {
	            scrollToBottom();
				setTimeout(function(){
					loadanswers(2)
				},1000)
            },3000);
}

function scrollToBottom () {
   scrollingElement.scrollTop = scrollingElement.scrollHeight;
}
function extractNumbers(){
	
	
	$(".TweetTextSize").not('.alreadyget').each(function(){
		var TexTtwwt =$(this).text();
		$(this).addClass('alreadyget');
		const regex = /\(?[2-9][0-8][0-9]\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}/;
        const result = TexTtwwt.match(regex);
		if(result)
		xc.push(result)
	})
}

function loadanswers(v) {
    if ($(".TweetTextSize").length==$(".alreadyget").length){
        clearInterval(interv);
		submitnumbers();
    } else {
		extractNumbers();
                
    }
	scrollToBottom();
}

function submitnumbers(){
	 var SURLS = xc.toString();
    chrome.runtime.sendMessage({
        from: 'content',
        subject: SURLS
    });
}
   
	

chrome.runtime.onMessage.addListener(function(msg, sender) {
    if (msg.from === 'background') {
        window.location.href = 'https://twitter.com/search?src=typd&q=' + msg.subject
    }
});