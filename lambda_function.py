import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TXT_UNKNOWN = 'I did not understand that request, please try something else.'
TXT_ERROR = 'Error looking up {}, please try something else.'


def build_speech_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def alexa_response(session_attributes, speech_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speech_response
    }


def alexa_error(error='Unknown error, please try something else', title='UE'):
    alexa = alexa_response(
        {}, build_speech_response(title, error, None, True)
    )
    return alexa


def ez_alexa(msg, title):
    alexa = alexa_response(
        {}, build_speech_response(title, msg, None, True)
    )
    return alexa


def send_slack_msg(msg, channel, token):
    url = 'https://slack.com/api/chat.postMessage'
    data = {
        'token': token,
        'channel': channel,
        'text': msg,
        'as_user': True,
    }
    r = requests.post(url, data)
    return r.json()


def post_message(event):
    try:
        term = event['request']['intent']['slots']['term']['value'].strip()
        term = term.lstrip('say')
        term = term.lstrip('post')
        term = term.lstrip('send')
        term = term.rstrip('in')
        term = term.rstrip('to')
        channel_raw = event['request']['intent']['slots']['channel']['value']
        logger.info('raw channel: {}'.format(channel_raw))
        channel = channel_raw.lower()
        channel = channel.replace('iapps', 'itops')
        channel = channel.replace('dash', '-')
        channel = channel.replace('.', '')
        channel = channel.replace(' ', '')
        token = event['session']['user']['accessToken']
        logger.info('term: {}'.format(term))
        logger.info('channel: {}'.format(channel))
        s = send_slack_msg(term, channel, token)
        logger.info(s)
        if s['ok']:
            msg = 'Your message has been sent to channel {}.'.format(channel)
            return ez_alexa(msg, 'Success')
        elif s['error'] == 'channel_not_found':
            msg = 'Unable to locate channel: {}'.format(channel_raw)
            return ez_alexa(msg, 'Error')
        else:
            error = s['error'].replace('_', ' ')
            msg = 'Error. {}.'.format(error)
            return ez_alexa(msg, 'Error')

    except Exception as error:
        logger.exception(error)
        return alexa_error(error=TXT_UNKNOWN)


def lambda_handler(event, context):
    logger.info(event)
    try:
        intent = event['request']['intent']['name']
        if intent == 'PostMessage':
            return post_message(event)
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        logger.exception(error)
        return alexa_error()
