import heroku3
import time
from dotenv import load_dotenv
import os

load_dotenv()
HEROKU_API_KEY = os.getenv('HEROKU_API_KEY')
heroku_conn = heroku3.from_key(HEROKU_API_KEY)
app = heroku_conn.apps()['minecraft-server-3']

while True:
    h = time.gmtime().tm_hour + 2
    if h < 2 or h > 10:
        time.sleep(3600)
    else:
        app.process_formation()['bot'].scale(0)
        time.sleep(3600*8)
        app.process_formation()['bot'].scale(1)
