import redis
import sys
import json

try:
    redisURL = sys.argv[1]
except:
    redisURL = input('Please input your redis url: ')

password, host, port = redisURL.replace(
    'redis://', '').replace('@', '|').replace(':', '|').split('|')
sql = redis.Redis(host=host, password=password, port=port, ssl=True)

try:
    with open('config.json', 'rt') as f:
        config = json.loads(f.read())
    if config == {'sessionid': '', 'steamRememberLogin': '', 'steamMachineAuth': '', 'steamLoginSecure': '', 'browserid': '', 'steamID64': ''}:
        print('You need to configure your steam information in config.json first!')
        sys.exit()
except FileNotFoundError:
    print('You need to create a config.json file and configure your steam information in it first!')
    sys.exit()

sql.set("steamCookie", json.dumps({"sessionid": config["steam"]["sessionid"], "steamRememberLogin": config["steam"]["steamRememberLogin"], f"steamMachineAuth{config['steam']['steamID64']}": config["steam"]
                    ["steamMachineAuth"], "steamLoginSecure": config["steam"]["steamLoginSecure"], "browserid": config["steam"]["browserid"]}))
sys.exit()