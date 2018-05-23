import threading
import time
import random
from datetime import datetime, timedelta
import dateutil.parser
import pytz

class Gene:
    def __init__(self, dna, occupied, time_penalty, tasks, flattened):
        self.dna = dna
        self.occupied = occupied
        self.time_penalty = time_penalty
        self.tasks = tasks
        self.penalty_value = None
        self.flattened = flattened
        self.N = len(occupied)
        self.m = len(flattened)


    def penalty(self):
        if self.penalty_value is None:
            self.penalty_value = self.calculate_penalty()
        return self.penalty_value

    def can_place(self, occ, pos, dura):
        for i in range(dura):
            if pos+i >= len(occ) or occ[pos+i]:
                return False
        return True

    def calculate_penalty(self):
        n = len(self.dna)
        occ = [] + self.occupied
        misplaced = 0
        for i, pos in enumerate(self.dna):
            task = self.tasks[self.flattened[i]]
            dura = task['duration_index']
            if self.can_place(occ, pos, dura):
                for i in range(dura):
                    occ[pos+i] = True
            else:
                misplaced += dura
                self.dna[i] = -1
        return misplaced * 1000

class GA:
    def __init__(self, occupied, time_penalty, tasks):
        self.occupied = occupied
        self.time_penalty = time_penalty
        self.tasks = tasks
        self.N = len(occupied)
        self.flattened = []
        for i, task in enumerate(tasks):
            self.flattened += [i for _ in range(task['repetition'])]
        self.m = len(self.flattened)

    def new_gene(self):
        dna = list(random.sample(range(self.N), self.m))
        return Gene(dna, self.occupied, self.time_penalty, self.tasks, self.flattened)

    def solve(self, timeout=180):
        best_gene = None
        for i in range(10000):
            gene = self.new_gene()
            if best_gene is None or best_gene.penalty() > gene.penalty():
                best_gene = gene
        result = []
        for ind, pos in enumerate(best_gene.dna):
            result.append((pos, self.flattened[ind]))
        return result

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
        for i in range(2*N):
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

        # due_index
        for i, task in enumerate(tasks):
            due_index = -1
            for j in range(N):
                if stamps[j] + timedelta(0, 1800) <= task['due']:
                    due_index = j
                else:
                    break
            tasks[i]['due_index'] = due_index
            tasks[i]['duration_index'] = int(tasks[i]['duration'] * 2)

        solution = self.solve_GA(occupied, penalty, tasks)
        for pos, ind in solution:
            if pos == -1:
                continue
            task = tasks[ind]
            dura = task['duration_index']
            result.append((stamps[pos], stamps[pos+dura], task['title']))

        result.sort()
        message = []
        for start, end, title in result:
            message.append('%02d:%02d~%02d:%02d : %s' % (start.hour, start.minute, end.hour, end.minute, title))
        send_text('\n'.join(message))
    
    def solve_GA(self, occupied, penalty, tasks):
        ga = GA(occupied, penalty, tasks)
        return ga.solve()

