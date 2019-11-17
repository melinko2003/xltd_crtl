import os, time, re, sys, requests
sys.path.append('lib/')
from slackclient import SlackClient
from leafly import Leafly

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """

    for event in slack_events:
        # Shows all events
        # print("Event Info: " + str(event))
        if event["type"] == "message" and not "subtype" in event:
            # print("Text Info: " + str(parse_direct_mention(event["text"])) + "\n" )
            # print("Context Info: " + str(event) + "\n")           
            user_id, message = parse_direct_mention(event["text"])
            # print(slack_client.api_call("users.info",user=event["user"])["user"]["name"])
            user = slack_client.api_call("users.info",user=event["user"])["user"]["name"]

            if user_id == starterbot_id:
                # print("Message Info: [" + str(user_id) + "/" + str(event["channel"]) + " ] " + str(message) + "\n" )
                return message, event["channel"], user

    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    msg = []

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "@" +user+ " Sure...write some more code then I can do that!"

    if command.lower().startswith("help"):
            response='''Supported features:
            donations:
                > @xlt bot donate
            leafly: Leafly search engine to search strains
                > @xlt bot leafly <your strain> : Your & related strain(s).
                > @xlt bot leafly help : This Menu.
            '''

    if command.lower().startswith("donate"):
            response='''This project runs on donations of time, money, crypto currency, and cpu cycles. Please consider 
donating to support this project! 

Crypto Currency [ Coinbase ]: https://commerce.coinbase.com/checkout/87daa8b6-6ac2-47b8-80e6-be5ed943de57
CPU Cycles [ Coinpot Webminer ]: https://coinpot.co/mine/dogecoin/?ref=8FDD19E61855
Venmo: @lcurran

If you would like to sponsor an offical feature or see a feature use the "bounty" feature. 
            '''

    if command.lower().startswith("bounty"):
        if command.split()[1] == 'help':
            response='''Supported "bounty" functions:
Add a Bounty:
@xlt bot bounty add_contract "add a feature"

Returns: <bounty_id>

Add a Payment to a Bounty:
@xlt bot bounty add_payment <bounty_id> <#> <currency>

Returns: <sponsor_id>
          
'''
#        elif command.split()[1] == 'add':
#            if command.split()[1] == 'contract':

#        elif command.split()[1] == 'add':
#            if command.split()[1] == 'contract':

#        elif command.split()[1] == 'remove':

#        elif command.split()[1] == 'accept':

        # if command.split()[1] == 'reject':


    # This is where you start to implement more commands!
    if command.lower().startswith("leafly"):
        method = command.split()
        requrl = 'http://127.0.0.1:5000/' + method[1] + "/"

        if command.split()[1] == 'help':
            # Help functions
            response='''Supported "Leafly" functions:
                @xlt bot leafly <your strain> : Your & related strain(s).
                @xlt bot leafly help : This Menu. '''
        
        if command.split()[1] == 'search':
            # http://127.0.0.1:5000/search/<your strain>
            resp = requests.get(requrl + command[7:])
            print(resp.json())
            response = "[ Strain: <" + resp.json()['url'] + "|" + resp.json()['strain'] +"> ]"

        if command.split()[1] == 'status':
            # http://127.0.0.1:5000/search/<your strain>
            resp = requests.get(requrl[:-1])
            print(resp.json())
            response = "[ Status: <" + requrl[:-1] + "|" + resp.json()['status'] +"> ]"     

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        print("[xltd_ctrl]: Online | BotID: " + str(starterbot_id))
        while True:
            command, channel, origin = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, origin)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
