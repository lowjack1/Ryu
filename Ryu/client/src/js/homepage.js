"use strict";

function CreateNewRoom() {
    let form_handle = $('input[name="username"]').parents('form');
    if(!form_handle[0].checkValidity()) {
        form_handle.find(':submit').click();
        return false;
    }

    let user_session_promise = createUserSession();
    Promise.resolve(user_session_promise).then(function(promise_resp) {
        let url = '/api?create_room';
        $.post(url, function(resp) {
            if(resp.status) {
                $('#chat_room_modal input[name="user_room"]').val(resp.result.data);
                $('#chat_room_modal input[name="user_room"]').attr('readonly', true);
                $('#chat_room_modal button[name="copy_btn"]').parent().show();
                $('#chat_room_modal .share-code-text').show();
                $('#chat_room_modal').modal('show');
            }
        });
    });
}

function showJoinRoomModal() {
    let form_handle = $('input[name="username"]').parents('form');
    if(!form_handle[0].checkValidity()) {
        form_handle.find(':submit').click();
        return false;
    }

    let user_session_promise = createUserSession();
    Promise.resolve(user_session_promise).then(function(promise_resp) {
        $('#chat_room_modal input[name="user_room"').val('');
        $('#chat_room_modal input[name="user_room"]').attr('readonly', false);
        $('#chat_room_modal button[name="copy_btn"]').parent().hide();
        $('#chat_room_modal .share-code-text').hide();
        $('#chat_room_modal').modal('show');
    });
}

function createUserSession() {
    let promise = new Promise(resolve => {
        let url = '/api?create_user_session';
        let username = $('input[name="username"]').val();
        $.post(url, {'username': username}, function(resp) {
            if(resp.status) {
                console.log("success");
            }
            resolve();
        });
    });
    return promise;
}

function CopyToClipboard() {
    $('input[name="user_room"]').select();
    document.execCommand("copy");
}