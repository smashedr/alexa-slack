import os
import requests
import logging

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


def coin_status(event):
    try:
        value = event['request']['intent']['slots']['currency']['value']
        value = value.lower().replace('define', '').strip()
        value = value.lower().replace('lookup', '').strip()
        value = value.lower().replace('look up', '').strip()
        value = value.lower().replace('search', '').strip()
        value = value.lower().replace('find', '').strip()
        logger.info('value: {}'.format(value))

    except Exception as error:
        logger.exception(error)
        return alexa_error(error=TXT_UNKNOWN)


def lambda_handler(event, context):
    logger.info(event)
    try:
        intent = event['request']['intent']['name']
        if intent == 'PostMessage':
            return ez_alexa('I am working.', 'Test')
        elif intent == 'CoinStatus':
            return coin_status(event)
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        logger.exception(error)
        return alexa_error()
