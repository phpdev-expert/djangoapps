chrome.runtime.onMessage.addListener(function(msg, sender) {
    if (msg.from === 'content') {
	    loadnewkeyword()
    }
});

function loadnewkeyword() {
    var xhttpget = new XMLHttpRequest();
    xhttpget.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var nkey = this.responseText;
            // alert('MSG'+nkey)
            if (nkey != 'null') {
                chrome.tabs.query({
                    active: true,
                    currentWindow: true
                }, function(tabs) {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        from: "background",
                        subject: nkey
                    }, function(response) {
                        console.log(response);
                    });
                });
            }
        }
    };
    xhttpget.open("GET", "https://nebu.herokuapp.com/api/categories/getAllCategoriesInTreeData", true);
    xhttpget.send();
}
