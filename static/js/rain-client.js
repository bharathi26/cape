$(function() {
    function handleResponse(response) {
            $("#rpc_response").html("Content: " + JSON.stringify(response));
            $("#status").html("Message received.");
        }
    
    function composeMsg(recipient, func, arg) {
    	$("#status").html("Composing Message.");
        // def __init__(self, sendernode="", sender="", recipientnode="", recipient="", func="", arg=None, error="", msg_type="request"):
        var msg = {'recipient': recipient,
                'func': func,
                'arg': arg
                };
        $("#rpc_request").html(msg);
        
        $.post('/rpc', msg, function(data) {
            handleResponse(data);
        }
        );
        
        $("#status").html("Message sent.");
        
    }

    $(document).ready(function () {
        // var nodename = {name: $("#nodename".val()}

        $("#status").html("The DOM is now loaded and can be manipulated.");
        
        composeMsg("REGISTRY", "rpc_listRegisteredComponents", "");
    })


    // When the testform is submitted…
    $("#testform").submit(function() {
        // post the form values via AJAX…
        var postdata = {name: $("#name").val()} ;
        $.post('/submit', postdata, function(data) {
            // and set the title with the result
            $("#title").html(data['title']) ;
           });
        composeMsg("REGISTRY", "rpc_listRegisteredComponents", "");
        return false ;
    });
    
    $(function() {
    	$( "input[type=submit_a], a, button" )
    	.button()
    	.click(function( event ) {
    	composeMsg("REGISTRY", "rpc_listRegisteredComponents", ""); //event.preventDefault();
    	});
    });
});