"Module for Emotion Recording"
import json

EMOTION_PLEASED = '[기쁨, 설렘, 상쾌함]'
EMOTION_PASSIONATE = '[신남, 즐거움, 열정적]'
EMOTION_SAD = '[슬픔, 후회, 우울]'
EMOTION_IRRITATED = '[짜증, 화남, 불쾌]'
EMOTION_COMPLEX = '[복합 감정]'
EMOTION_ETC = '[기타 감정]'
EMOTION_ORDINARY = '[평범하다]'
EMOTIONS = [EMOTION_PLEASED, EMOTION_PASSIONATE,
            EMOTION_SAD, EMOTION_IRRITATED, EMOTION_COMPLEX,
            EMOTION_ETC, EMOTION_ORDINARY]
REPLYS = [
    '헤헤, 잘됐네요.',
    '냥! 저도 즐거운데요?',
    '그렇군요 ㅠㅠ',
    '날리냥도 화가 나네요!',
    '어떤 감정인가요?',
    '어떤 감정인가요?',
    '그럴 때가 많지요.'
]


KEYBOARD_EMOTIONS = [
    [EMOTION_PLEASED],
    [EMOTION_PASSIONATE],
    [EMOTION_SAD],
    [EMOTION_IRRITATED],
    [EMOTION_COMPLEX, EMOTION_ETC, EMOTION_ORDINARY]
    ]

KEYBOARD = json.dumps({
    "keyboard" : KEYBOARD_EMOTIONS,
    "one_time_keyboard" : True,
    })

def is_emorec_response(message):
    "determines if message is emorec response"
    return message["data"]["text"] in EMOTIONS
