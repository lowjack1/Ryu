import aiohttp
from tornado.ioloop import IOLoop
from tornado.web import HTTPError, RequestHandler

class BaseHandler(RequestHandler):
    async def prepare(self):
        ''' Overriding prepare() to set current user and his room from the cookie '''

        self.current_user = None
        self.current_user_name = None
        self.room = None

        # Set current user
        user_cookie = self.get_secure_cookie('user')
        if user_cookie:
            user_id, token = user_cookie.decode().split(';')
            user_id = int(user_id)

            async with self.settings['pool'].acquire() as connection:
                q = "SELECT ID, token, name FROM ryu_user WHERE ID=$1;"
                res = await connection.fetchrow(q, user_id)

            if res and res['token'] == token:
                self.current_user = res['id']
                self.current_user_name = res['name']

            else:
                self.clear_cookie('user')

        # Set user room
        user_room = self.get_secure_cookie('room')
        if user_room:
            room_id = int(user_room.decode())
            async with self.settings['pool'].acquire() as connection:
                q = "SELECT room_exit FROM ryu_room WHERE ID=$1;"
                room_exit = await connection.fetchval(q, room_id)

            if room_exit is not None and room_exit == 0:
                self.room = room_id
        else:
            self.clear_cookie('room')


    def write_api_response(self, data, status=True, msg="", code=None):
        '''
        Function to generate a standard response for API calls
        '''
        status = True if status == True else False
        if code is None:
            code = 200 if status else 400
        resp = {
            "status": status,
            "code": code,
            "msg": msg,
            "result": {'user': None, 'data': data} if status else None
        }

        # Update user data if user is known
        if status and self.current_user:
            resp['result']['user'] = {
                "name": self.current_user_name,
            }
        self.write(resp)

    def set_user_room(self, room):
        self.set_secure_cookie('room', str(room))