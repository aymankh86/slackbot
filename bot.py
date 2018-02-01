import slackclient
import time
import json
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


with open('./data.json') as f:
    available_commands = json.load(f)


def help():
    commands = '\n'.join(available_commands.keys())
    return "*Available Commands*:\n```%s```" % commands


TOKEN = os.environ.get('SLACK_BOT_TOKEN')
ID = os.environ.get('SLACK_BOT_ID')
SOCKET_DELAY = 1

slack_client = slackclient.SlackClient(TOKEN)


def user_name(id):
    try:
        return slack_client.api_call(
            'users.info', user=id)['user']['real_name']
    except KeyError:
        return None


def is_hi(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in [
        'hello', 'bonjour', 'hey', 'hi', 'sup',
        'morning', 'hola', 'ohai', 'yo', 'merhaba', 'selam'])


def is_bye(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in [
        'bye', 'goodbye', 'revoir', 'adios',
        'later', 'cya', 'gule gule', 'thanks', 'hoşçakal'])


def say_hi(user):
    return 'Hi, *{}*! How could I help you?'.format(user)


def say_bye(user):
    return 'Bye {}!'.format(user)


def is_message(event):
    return event.get('type') and event.get('type') == 'message'


def is_private(event):
    return event.get('channel') and event.get('channel').startswith('D')


def me(event):
    return event.get('user') and event.get('user') == ID


def handle_event(event):
    text = event.get('text')
    from_user = user_name(event.get('user'))
    if is_hi(text):
        message = say_hi(from_user)
        return '%s\n\n%s' % (message, help())
    elif is_bye(text):
        return say_bye(from_user)
    elif text.strip() not in available_commands.keys():
        return help()
    else:
        return available_commands[event.get('text').strip()]


def run():
    if slack_client.rtm_connect():
        logger.info('[.] chatbot is ON...')
        while True:
            event_list = slack_client.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    if is_message(event) and is_private(event) and\
                            not me(event):
                        logger.info(event)
                        slack_client.api_call(
                            'chat.postMessage',
                            channel=event.get('channel'),
                            text=handle_event(event),
                            as_user=True)

            time.sleep(SOCKET_DELAY)
    else:
        print('[!] Connection to Slack failed')


if __name__ == '__main__':
    run()
