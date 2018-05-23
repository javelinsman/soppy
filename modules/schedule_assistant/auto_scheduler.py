import threading
import time
import random
from datetime import datetime, timedelta
import dateutil.parser
import pytz

class AutoScheduler:
    def __init__(self):
        pass
    def schedule(self, events, tasks, send_text):
        code = random.randint(1000, 9999)
        send_text('요청번호 %d번으로 계산을 시작했어요. 결과가 나오면 바로 전해드릴게요!' % code)
        threading.Thread(target=self.optimize, args=(events, tasks, send_text, code)).start()
    def optimize(self, events, tasks, send_text, code):
        #N = 21 * 24 * 2
        N = 1 * 12 * 2
        now = datetime.now()
        stamp_base = datetime(now.year, now.month, now.day, now.hour, 0, 0)
        if now.minute >= 30:
            stamp_base = stamp_base + timedelta(0, 3600)
        # stamp
        stamps = []
        for i in range(N):
            stamps.append(pytz.timezone('Asia/Seoul').localize(stamp_base + timedelta(0, 1800 * i)))
        # occupied
        occupied = [False] * N
        ind = 0
        result = []
        for event in events:
            if 'dateTime' not in event['start']:
                continue
            if 'dateTime' not in event['end']:
                continue
            start = dateutil.parser.parse(event['start']['dateTime'])
            end = dateutil.parser.parse(event['end']['dateTime'])
            title = event['summary'] if 'summary' in event else '(제목 없음)'
            result.append((start, end, title))
            while ind < N and stamps[ind] < start:
                ind += 1
            while ind < N and stamps[ind] < end:
                occupied[ind] = True
                ind += 1
            if ind >= N:
                break
        # penalty
        penalty = [0] * N
        for i in range(N):
            if 22 <= stamps[i].hour <= 23:
                penalty[i] = 10
            elif 0 <= stamps[i].hour <= 6:
                penalty[i] = 50

        solution = self.solve_GA(occupied, penalty, tasks)
        for pos, ind in solution:
            task = tasks[ind]
            dura = int(task['duration'] * 2)
            result.append((stamps[pos], stamps[pos+dura], task['title']))

        result.sort()
        message = []
        for start, end, title in result:
            message.append('%02d:%02d~%02d:%02d : %s' % (start.hour, start.minute, end.hour, end.minute, title))
        send_text('\n'.join(message))
    
    def solve_GA(self, occupied, penalty, tasks):
        N = len(occupied)
        flattened = []
        for i, task in enumerate(tasks):
            flattened += [i for _ in range(task['repetition'])]
        m = len(flattened)
        while True:
            gene = random.sample(range(N), m)
            feasible = True
            occ = [] + occupied
            for i, pos in enumerate(gene):
                dura = int(tasks[flattened[i]]['duration'] * 2)
                for j in range(dura):
                    if occ[pos+j]:
                        feasible = False
                        break
                    occ[pos+j] = True
                if not feasible:
                    break
            if feasible:
                break
        ret = []
        for i, pos in enumerate(gene):
            ret.append((pos, flattened[i]))
        return ret
