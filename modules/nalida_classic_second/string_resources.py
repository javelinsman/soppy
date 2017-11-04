"""
String Resourses for NalidaClassicSecond module
"""

def multi(*args):
    "use this function when you want to send multple messages"
    delimiter = '$$$'
    return delimiter.join(args)

COMMAND_PUBLISH_REGISTRATION_KEY = '등록키발급'
COMMAND_MAKE_SESSION = '세션등록'

REGISTER_COMPLETE = multi(
    '안녕하세요!',
    '헤헤, 반가워요. 저는 날리다의 마스코트이자 날리다 클래식 워크샵의 진행을 도울 날리냥이라고 해요.',
    '앞으로 한 달 동안 날리다와 함께 소중한 시간 보내시길 바라요.',
    )

ASK_NICKNAME = '우선 진행을 하기에 앞서서 참가자님을 뭐라고 불러야 할지를 알고 싶어요. 오늘 워크샵에서 정하신 별칭이 뭐예요?'
CONFIRM_NICKNAME = '아래의 별명이 맞나요? "네", "아니오"로 대답해주세요.\n[%s]'
RESPONSE_NICKNAME_YES = '네'
RESPONSE_NICKNAME_NO = '아니오'
WRONG_RESPONSE_FORMAT = '잘못된 형식의 답변입니다.'
NICKNAME_SUBMITTED = '이제부터 %s님이라고 부를게요'
ASK_NICKNAME_AGAIN = '그럼 뭐예요?'
ASK_EXPLANATION_FOR_NICKNAME = '별명 왜 그렇게 지었어요? 2~3문장으로 답변해주세요.'
EXPLANATION_SUBMITTED = '좋은 설명 잘 들었어요!'
ASK_GOAL_NAME = '4주 동안 이룰 목표 이름을 알려주세요'
ASK_GOAL_DESCRIPTION = '4주 동안 이룰 목표 설명을 알려주세요'
GOAL_NAME_SUBMITTED = '좋은 목표 이름 잘 들었어요!'
GOAL_DESCRIPTION_SUBMITTED = '좋은 목표 설명 잘 들었어요!'
INSTRUCTIONS_FOR_GOAL = '이제부터 매일 사진을 올리시면 그것이 반영될 거예요'
INSTRUCTIONS_FOR_EMOREC = '그리고 오늘부터 매일 3번씩 감정을 물어볼 거예요'

GOAL_SHARING_MESSAGE = '%s님의 목표 인증샷'
ASK_GOAL_ACHIEVEMENT_DETAIL = '굳. 소감 좀 자세히 말해줄래?'
GOAL_SHARING_DETAILED_MESSAGE = '%s님의 목표 설명: %s'
COMMAND_NOT_TO_SHARE_GOAL = '비공개'
GOAL_RESPONSE_RECORDED_AND_SHARED = '응답이 기록되고 공유되었어요. 감사합니다!'
GOAL_RESPONSE_RECORDED_BUT_NOT_SHARED = '응답이 기록되고 공유는 되지 않았어요. 감사합니다!'

RESPONSE_RECORDED = '응답이 기록되었어요. 감사합니다!'

ASK_EMOTION = '지금은 무슨 감정을 느끼고 있나요?\n메세지를 늦게 보았어도 현재의 상태를 기록해주세요.'
ASK_EMOTION_DETAIL = '감정을 더 자세히 알려주세요.'
EMOREC_SHARING_MESSAGE = '누군가의 현재 감정: %s'
EMOREC_SHARING_DETAILED_MESSAGE = '감정 설명: %s'
COMMAND_NOT_TO_SHARE_EMOTION = '비공개'
EMOREC_RESPONSE_RECORDED_AND_SHARED = '응답이 기록되고 공유되었어요. 감사합니다!'
EMOREC_RESPONSE_RECORDED_BUT_NOT_SHARED = '응답이 기록되고 공유는 되지 않았어요. 감사합니다!'

ASK_GOAL_RESPONSE_CONFIRMATION = '이 사진이 오늘의 목표 인증샷이 맞나요?'
RESPONSE_GOAL_YES = '네'
REQUEST_ANOTHER_PICTURE = '그럼 나중에 다시 올려주세요!'

ERROR_MAKE_SESSION_INVALID_CONTEXT = '잘못된 아이디가 포함되어 있습니다. 다시 확인해주세요.'
ERROR_MAKE_SESSION_NO_TARGET_CHAT = '중계방이 등록되지 않은 사용자가 있습니다. 다시 확인해주세요.'
COMMAND_PREFIX_REGISTER_BROADCASTING_ROOM = 'REGBCROOM:'
REGISTERED_AS_BROADCASTING_ROOM = '이 곳이 %s님의 중계방으로 등록되었습니다. 감사합니다.'
