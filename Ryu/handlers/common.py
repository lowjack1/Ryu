import os
from datetime import datetime, timedelta
from dateutil import tz

import aiohttp
from tornado.web import HTTPError, escape
from tornado.ioloop import IOLoop
import tornado.websocket
import tornado.escape

from uuid import uuid4

from .base import BaseHandler

class HomePage(BaseHandler):
    async def get(self):
        return self.render("homepage.html")


class UserRoom(BaseHandler):
    async def get(self):
        if self.current_user is None:
            # User information is unknown, redirect to homepage
            return self.redirect("/")

        if self.room is None:
            return self.redirect("/invalid_room")

        rdata = {
            'user_id': self.current_user,
            'username': self.current_user_name,
            'room': self.room
        }

        return self.render("user_room.html", rdata=rdata)


class WebSocket(tornado.websocket.WebSocketHandler, BaseHandler):
    # class variable to store mapping of users and their room
    # Room will be the key and it is mapped with the list of user who are connected to it
    user_connection_dict = dict()

    async def open(self):
        if self.room not in self.user_connection_dict:
            self.user_connection_dict[self.room] = set()

        # Add current user to the client
        if self not in self.user_connection_dict[self.room]:
            self.user_connection_dict[self.room].add(self)

            async with self.settings['pool'].acquire() as connection:
                async with connection.transaction():
                    # Add user entry with its room in the table "ryu_user_room_map"
                    q = "INSERT INTO ryu_user_room_map (user_id, room_id) VALUES($1, $2);"
                    await connection.execute(q, self.current_user, self.room)

                    # Get all user in the current room to update total user which are in the chat room
                    q = '''
                        SELECT RU.ID, RU.name
                        FROM ryu_user AS RU
                        INNER JOIN ryu_user_room_map AS RURM ON RU.ID=RURM.user_id
                        WHERE RURM.room_id=$1
                        ORDER BY RU.name;
                        '''
                    res = await connection.fetch(q, self.room)
                    users_list = [[_['id'], _['name']] for _ in res]

                    # Get latest 10 msg from the room
                    q = '''
                        SELECT RU.ID, RU.name, RC.msg
                        FROM ryu_conversation AS RC
                        INNER JOIN ryu_user AS RU ON RU.ID=RC.user_id
                        WHERE room_id=$1
                        ORDER BY RC.date_sent DESC LIMIT 10;
                        '''
                    res = await connection.fetch(q, self.room)
                    messages = [(_['id'], _['name'], _['msg']) for _ in res]

            # Update list of users to all client
            msg_body = {
                'user_id': self.current_user,
                'usernames': users_list,
                'messages': messages,
                'new_user_joined': 1,
            }

            [client.write_message(msg_body) for client in self.user_connection_dict[self.room]]

    async def on_message(self, msg_body):
        msg_body = tornado.escape.json_decode(msg_body)

        async with self.settings['pool'].acquire() as connection:
            q = "INSERT INTO ryu_conversation (user_id, room_id, msg) VALUES ($1, $2, $3);"
            await connection.execute(q, self.current_user, self.room, msg_body['message'])

        [client.write_message(msg_body) for client in self.user_connection_dict[self.room]]


    def on_close(self):
        IOLoop.current().spawn_callback(self.user_left)

    async def user_left(self):
        # Delete user from the dictionary
        self.user_connection_dict[self.room].remove(self)

        async with self.settings['pool'].acquire() as connection:
            async with connection.transaction():
                # Remove current user entry from the table
                q = "DELETE FROM ryu_user_room_map WHERE user_id=$1 AND room_id=$2;"
                await connection.execute(q, self.current_user, self.room)

                if len(self.user_connection_dict[self.room]) == 0:
                    # If no user exist in the room then exit room
                    del self.user_connection_dict[self.room]
                    # Exit room
                    q = "UPDATE ryu_room SET room_exit=$1 WHERE ID=$2;"
                    await connection.execute(q, True, self.room)
                else:
                    # Broadcast this is to each user in the room
                    msg_body = {
                        'user_id': self.current_user,
                        'username': self.current_user_name,
                        'user_left': 1,
                    }
                    [client.write_message(msg_body) for client in self.user_connection_dict[self.room]]


class APIHandler(BaseHandler):
    async def post(self):
        if self.get_argument('create_room', None) is not None:
            async with self.settings['pool'].acquire() as connection:
                async with connection.transaction():
                    # CREATE record of room
                    q = "INSERT INTO ryu_room (user_id) VALUES ($1) RETURNING ID;"
                    room_id = await connection.fetchval(q, self.current_user)

            # Set current room of the user
            self.set_user_room(room_id)
            return self.write_api_response(room_id)


        if self.get_argument('join_room', None) is not None:
            room_id = int(self.get_body_argument('user_room'))
            async with self.settings['pool'].acquire() as connection:
                q = "SELECT room_exit FROM ryu_room WHERE ID=$1;"
                room_exit = await connection.fetchval(q, room_id)

            if room_exit is None or room_exit == True:
                return self.redirect("/invalid_room")

            # Set current room of the user
            self.set_user_room(room_id)

            # Redirect user to the room
            return self.redirect('/room?%s' % room_id)


        if self.get_argument('create_user_session', None) is not None:
            user = self.get_body_argument('username')
            token = uuid4().hex
        
            async with self.settings['pool'].acquire() as connection:
                async with connection.transaction():
                    # CREATE record of user
                    q = "INSERT INTO ryu_user (name, token) VALUES ($1, $2) RETURNING ID;"
                    user_id = await connection.fetchval(q, user, token)

            auth_data_raw = "%s;%s" % (user_id, token)
            self.set_secure_cookie('user', auth_data_raw)
            return self.write_api_response(1)


class InvalidRoom(BaseHandler):
    def get(self):
        self.render("invalid_room.html")


class Default404Handler(BaseHandler):
    def get(self):
        self.set_status(404)
        self.render("404.html")