import threading
import time
import random

class AutoScheduler:
    def __init__(self):
        pass
    def schedule(self, events, tasks, send_text):
        code = random.randint(1000, 9999)
        send_text('요청번호 %d번으로 계산을 시작했어요. 결과가 나오면 바로 전해드릴게요!' % code)
        threading.Thread(target=self.optimize, args=(events, tasks, send_text, code)).start()
    def optimize(self, events, tasks, send_text, code):
        time.sleep(15)
        send_text('%d번 요청 계산 완료! 짜잔!!' % code)
