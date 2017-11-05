"""
String Resourses for NalidaClassicSecond module
"""

# 메시지를 여러 개로 끊고 싶을 때는 이 함수를 사용하세요.
# 아래의 예시 참조.
def multi(*args):
    "use this function when you want to send multple messages"
    delimiter = '$$$'
    return delimiter.join(args)

# 처음에 등록하는 과정
REGISTER_COMPLETE = multi(
    '안녕하세요!',
    '헤헤, 반가워요. 저는 날리다의 마스코트이자 날리다 클래식 워크샵의 진행을 도울 날리냥이라고 해요.',
    '앞으로 한 달 동안 날리다와 함께 소중한 시간 보내시길 바라요.',
    )

ASK_NICKNAME = '우선 진행을 하기에 앞서 참가자님을 어떻게 부르면 좋을지 알고 싶어요. 오늘 워크샵에서 정하신 별칭이 뭐예요?'
CONFIRM_NICKNAME = '아래의 별칭이 맞나요? "네", "아니오"로 대답해주세요.\n[%s]'
RESPONSE_NICKNAME_YES = '네'
RESPONSE_NICKNAME_NO = '아니오'
WRONG_RESPONSE_FORMAT = '잘못된 형식의 답변입니다.'
NICKNAME_SUBMITTED = '이제부터 %s님이라고 부를게요!'
ASK_NICKNAME_AGAIN = '그럼 뭐예요?'
ASK_EXPLANATION_FOR_NICKNAME = '이런 별칭을 짓게 되신 계기는 무엇인가요? 2~3문장으로 답변해주세요.'
EXPLANATION_SUBMITTED = '좋은 설명 잘 들었어요!'
ASK_GOAL_NAME = multi(
	'날리다 워크샵을 진행하는 4주 동안 각자의 목표를 설정해서 함께 달성해보려고 해요.',
	'4주동안 이루고 싶은 목표를 정하고 이름을 지어서 알려주세요. 설명은 생략하고 이름만요!'
	)
GOAL_NAME_SUBMITTED = '오오, 정말 재미있어 보이는 목표네요!'
ASK_GOAL_DESCRIPTION = '어떤 내용인지 정말 궁금한데요? 이제 목표에 대해서 더 자세히 설명해주시겠어요?'
GOAL_DESCRIPTION_SUBMITTED = '헤헤. 설명 잘 들었어요. 꼭 목표를 달성하실 수 있기를 바랄게요.'
INSTRUCTIONS_FOR_GOAL = '진행자님들이 설명하신 것처럼 오늘부터 실천한 목표의 인증샷을 매일 찍어서 서로 공유하려고 해요. 지금 저와 얘기하고 있는 이 방에 사진을 올리면 된답니다.'
INSTRUCTIONS_FOR_EMOREC = '그리고 오늘부터 하루에 3번씩 랜덤한 시각에 지금 어떤 감정을 느끼고 있는지를 물어볼 거예요. 나의 감정을 파악하는 데 도움이 되는 활동이니까 성실하게 답변해주시기를 바라요. 지금 바로 한번 연습해 볼까요?.'

# 목표 인증샷
ASK_GOAL_RESPONSE_CONFIRMATION = '이 사진이 오늘의 목표 인증샷이 맞나요? 맞으면 "네"라고 말해주세요.'
RESPONSE_GOAL_YES = '네'
REQUEST_ANOTHER_PICTURE = '그럼 나중에 다시 올려주세요!'
GOAL_SHARING_MESSAGE = '%s님의 목표 인증샷\n[%s]'
ASK_GOAL_ACHIEVEMENT_DETAIL = '잘하셨어요. 오늘 목표를 달성하면서 느끼신 소감을 간단히 알려주실래요?'
GOAL_SHARING_DETAILED_MESSAGE = '%s님의 목표 설명: %s'
GOAL_RESPONSE_RECORDED_AND_SHARED = '응답이 기록되고 공유되었어요. 감사합니다!'
GOAL_RESPONSE_RECORDED_BUT_NOT_SHARED = '응답이 기록되고 공유는 되지 않았어요. 감사합니다!'
COMMAND_NOT_TO_SHARE_GOAL = '비공개' #노터치

# 감정기록
ASK_EMOTION = '지금은 무슨 감정을 느끼고 있나요?\n메시지를 늦게 보았어도 현재의 상태를 기록해주세요.'
EMOREC_SHARING_MESSAGE = '지금 어떤 동료는 이름 감정을 느끼고 있대요: %s'
ASK_EMOTION_DETAIL = '감정을 더 자세히 설명해주세요.'
EMOREC_SHARING_DETAILED_MESSAGE = '감정 설명: %s'
EMOREC_RESPONSE_RECORDED_AND_SHARED = '응답이 기록되고 공유되었어요. 감사합니다!'
EMOREC_RESPONSE_RECORDED_BUT_NOT_SHARED = '응답이 기록되고 공유는 되지 않았어요. 감사합니다!'
COMMAND_NOT_TO_SHARE_EMOTION = '비공개' #노터치

# 기타
CAT_MEOWS = ['냥', '야옹', '냐옹', '야아옹', '냐아옹']

# Admin 방
REGISTERED_AS_BROADCASTING_ROOM = '이 곳이 %s님의 중계방으로 등록되었습니다. 감사합니다.'
# 이 밑으론 아마 건드릴 거 없을 듯.
ERROR_MAKE_SESSION_INVALID_CONTEXT = '잘못된 아이디가 포함되어 있습니다. 다시 확인해주세요.'
ERROR_MAKE_SESSION_NO_TARGET_CHAT = '%s님의 중계방이 등록되지 않았습니다. 다시 확인해주세요.'
ERROR_NOTICE_INVALID_CONTEXT = '잘못된 닉네임이 포함되어 있습니다. 다시 확인해주세요.'
COMMAND_PUBLISH_REGISTRATION_KEY = '등록키발급'
COMMAND_MAKE_SESSION = '세션등록'
COMMAND_NOTICE = '공지'
REPORT_NOTICE_COMPLETE = '공지를 완료했습니다!'
COMMAND_PREFIX_REGISTER_BROADCASTING_ROOM = 'REGBCROOM:' #절대노터치

# 모니터링
REPORT_NICKNAME = '사용자 %s가 닉네임을 등록했습니다: %s'
HELP_MESSAGE_BROADCASTING_ROOM_REGKEY = multi(
    '%s님의 중계방을 등록하려면 아래의 메세지를 직접 보내게 하세요',
    'REGBCROOM:%s'
    )
REPORT_EXPLANATION = '%s님의 별명 설명: %s'
REPORT_GOAL_NAME = '%s님의 목표 이름: %s'
REPORT_GOAL_DESCRIPTION = '%s님의 목표 설명: %s'
REPORT_EMOREC_SHARING = '%s님의 감정: %s'
REPORT_EMOREC_DETAIL = '%s님의 감정설명: %s'
