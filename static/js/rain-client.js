$(function() {
    function handleResponse(response) {
    	// Handle responses from outgoing messages.
        $("#rpc_responses").append("<br />" + response);
        $("#status").html("Message received.");

        msg = jQuery.parseJSON(response);
        // TODO: Actually it should be unnecessary to convert to and from
        // JSON all the time, jQuery and Cherrypy are both capable of
        // native JSON handling. Somehow POSTs vanish in 404's and other
        // weird stuff happens when using that.

        // Exemplary Wiki response handler
        if (msg["func"] == "getPage") {
        	$("#wikicontent").html(msg["arg"]);
        	$("#edit_page").show();
        }
        
        if (msg["func"] == "editPage") {
        	$("#wikisource").val(msg["arg"]);
        	
        }
        
        if (msg["func"] == "storePage") {
			composeMsg("wiki", "getPage", {'pagename': $("#name").val()});
		}
        
        if (msg["sender"] == "wiki") {}
        // TODO: This doesn't work, since the senders name is his real
        // complex name, "wiki" only its directory name.
        
        if (document.readyState === "complete") {
        	$("#rpc_log").accordion("refresh");
        }
    }
    
    function composeMsg(recipient, func, arg) {
    	// Composes and sends a Message to the hosting RAIN Node.
    	$("#status").html("Composing Message.");
        
    	// Compose Message
        var msg = {'recipient': recipient,
                'func': func,
                'arg': arg
                };
        
        // Transmit and wait for a reply
        $.ajax({
        	type: "POST",
        	url: '/rpc',
        	data: JSON.stringify(msg),
        	success: function(data) {
        		handleResponse(data);
        	},
        	contentType: 'application/json',
        	dataType: 'text'
        	});
        
        $("#status").html("Message sent.");
        $("#rpc_requests").append("<br />" + JSON.stringify(msg));
        
        if (document.readyState === "complete") {
        	$("#rpc_log").accordion("refresh");
        }
    }

    $(document).ready(function () {
        $("#status").html("Ready.");
        $("#edit_page").hide();
        // On load, retrieve index page from wiki. Just for demoing purposes.        
        //composeMsg("wiki", "getPage", {'pagename': "index"});
    });
    
    $(function() {
    	// RPC Log sits in an height filled accordion
	    $("#rpc_log").accordion({
	    	heightStyle: "fill"
	    });
	});
    
    $(function() {
    	$("#save_page")
    	.button()
    	.click(function( event ) {
    		pagename = $("#name").val();
    		content = $("#wikisource").val();
    		
    		composeMsg("wiki", "storePage", {'pagename': pagename, 'content': content});
    	});
    });

    $(function() {
    	// Button to retrieve named Wiki page
    	$("#get_page" )
    	.button()
    	.click(function( event ) {
    		pagename = $("#name").val();
    		
    		composeMsg("wiki", "getPage", {'pagename': pagename});
    	});
    });
    
    $(function() {
    	// Button to retrieve editable content
    	$("#edit_page")
    	.button()
    	.click(function(event) {
    		pagename = $("#name").val();
    		
    		composeMsg("wiki", "editPage", {'pagename': pagename});
    	});
    });
});