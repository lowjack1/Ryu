ryu_user = '''
CREATE TABLE ryu_user (
    ID SERIAL NOT NULL,
    name VARCHAR (255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    date_join TIMESTAMP WITH TIME ZONE DEFAULT (now() AT TIME ZONE 'UTC') NOT NULL,
    PRIMARY KEY (ID)
);
'''

'''
Store information of which user has created the room
TODO : alter ryu_room to start id from 12345
alter SEQUENCE ryu_room_id_seq RESTART with 12345;
'''
ryu_room = '''
CREATE TABLE ryu_room (
    ID SERIAL NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE DEFAULT (now() AT TIME ZONE 'UTC') NOT NULL,
    user_id INTEGER NOT NULL,
    room_exit BOOLEAN NOT NULL,
    PRIMARY KEY(ID),
    FOREIGN KEY (user_id) REFERENCES ryu_user(ID)
);
'''

ryu_user_room_map = '''
CREATE TABLE ryu_user_room_map (
    ID SERIAL NOT NULL,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_join TIMESTAMP WITH TIME ZONE DEFAULT (now() AT TIME ZONE 'UTC') NOT NULL,
    PRIMARY KEY(ID),
    FOREIGN KEY (user_id) REFERENCES ryu_user(ID),
    FOREIGN KEY (room_id) REFERENCES ryu_room(ID)
);
'''

ryu_conversation = '''
CREATE TABLE ryu_conversation (
    ID SERIAL NOT NULL,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    msg TEXT,
    date_sent TIMESTAMP WITH TIME ZONE DEFAULT (now() AT TIME ZONE 'UTC') NOT NULL,
    PRIMARY KEY(ID),
    FOREIGN KEY (user_id) REFERENCES ryu_user(ID),
    FOREIGN KEY (room_id) REFERENCES ryu_room(ID)
);
'''

async def addDatabaseTables(pool):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(ryu_user)
            await connection.execute(ryu_room)
            await connection.execute(ryu_user_room_map)
            await connection.execute(ryu_conversation)
            


async def main(PG_CONFIG):
    pool = await asyncpg.create_pool(PG_CONFIG['dsn'])
    await addDatabaseTables(pool)

import asyncio
import asyncpg
from dotenv import load_dotenv
from os import getenv
from os.path import dirname, join, exists

import aiohttp
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

PG_CONFIG = {
    'user': getenv('DB_USER'),
    'pass': getenv('DB_PASS'),
    'host': getenv('DB_HOST'),
    'database': getenv('DB_NAME'),
    'port': getenv('DB_PORT')
}
PG_CONFIG['dsn'] = "postgres://%s:%s@%s:%s/%s" % (PG_CONFIG['user'], PG_CONFIG['pass'],
                                                PG_CONFIG['host'], PG_CONFIG['port'], PG_CONFIG['database'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(PG_CONFIG))
