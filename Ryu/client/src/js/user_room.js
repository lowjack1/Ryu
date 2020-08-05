var url = `ws://${location.host}/websocket`;
var ws = new WebSocket(url);

function sendMessage() {
    let msg_input_el = $('input[name="msg_input"]');
    let message = msg_input_el.val().trim();
    
    if(message == '') {
        return;
    }

    let user_id = parseInt($('input[name="user_id"]').val());
    let username = $('input[name="username"]').val();
    let userroom = $('input[name="userroom"]').val();

    let payload = {
        "user_id": user_id,
        "username": username,
        "room": userroom,
        "message": message,
    };

    // Make the request to the WebSocket.
    ws.send(JSON.stringify(payload));
    // Clear the message from the input.
    msg_input_el.val('');
    return false;
}

ws.onmessage = function(evt) {
    let messageDict = JSON.parse(evt.data);
    let user_id = $('input[name="user_id"]').val();

    if('new_user_joined' in messageDict) {
        showNewUserJoined(messageDict);
        updateMessages(messageDict, user_id);
    } else if('user_left' in messageDict) {
        removeUser(messageDict);
    } else {
        showCurrentMessage(messageDict, user_id);
    }
};

function updateMessages(msg_obj, current_user_id) {
    if(current_user_id != msg_obj.user_id) {
        // Show all messages only to user who has just enters the room
        return ;
    }
    console.log(msg_obj.messages);
    let html = "";
    $.each(msg_obj.messages, function(_, data) {
        let user_id = data[0];
        let username = data[1];
        let msg = data[2];

        html += `
            <div class="card msg-width ${user_id ==  current_user_id? 'sent-msg': ''}">
                <div class="card-header bg-primary">
                    ${username}
                </div>
                <div class="card-body">
                    ${msg}
                </div>
            </div>`;
    });
    $('.chat').append(html);
    $(".chat").animate({ scrollTop: $('.chat').prop("scrollHeight")}, 500);
}

function removeUser(messageDict) {
    let username = messageDict.username;
    let user_id = messageDict.user_id;

    $(`.${username}-${user_id}`).remove();
}

function showNewUserJoined(messageDict) {
    let html = "";
    $.each(messageDict.usernames, function(_, data) {
        let user_id = data[0];
        let username = data[1];
        html += `
            <div class="col-12 text-center mb-2 ${username}-${user_id}">
                <span class="user-label">${username}</span>
            </div>`;
    });
    $('.new-user-div').html(html);
}

function showCurrentMessage(messageDict, current_user_id) {
    // Create a div for the user message
    let msg_html = `
        <div class="card msg-width ${messageDict.user_id == current_user_id ? 'sent-msg': ''}">
            <div class="card-header bg-primary">
                ${messageDict.username}
            </div>
            <div class="card-body">
                ${messageDict.message}
            </div>
        </div>`;
    $('.chat').append(msg_html);
    $(".chat").animate({ scrollTop: $('.chat').prop("scrollHeight")}, 500);
}

// ######################################### EVENT LISTENER ##############################################

$('button[name="msg_sent_btn"').on('click', sendMessage);

$('input[name="msg_input"]').on('keyup',function(event){
    if(event.keyCode == 13){
      sendMessage();
    }
});
