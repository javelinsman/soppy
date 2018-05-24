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
        occ = [] + self.occupied
        # misplaced
        misplaced = 0
        for i, pos in enumerate(self.dna):
            task = self.tasks[self.flattened[i]]
            dura = task['duration_index']
            due_index = task['due_index']

            if pos + dura - 1 <= due_index and self.can_place(occ, pos, dura):
                for j in range(dura):
                    occ[pos+j] = True
            else:
                misplaced += dura
                self.dna[i] = -1
        # time_penalty
        time_penalty_value = 0
        for i in range(self.N):
            if occ[i]:
                time_penalty_value += self.time_penalty[i]

        # imbalance
        workloads = [0]
        for i in range(self.N):
            if i > 0 and self.time_penalty[i] == 1 and self.time_penalty[i-1] > 1:
                workloads.append(0)
            if occ[i]:
                workloads[-1] += 1
        mean = sum(workloads) / len(workloads)
        variance = 0
        for workload in workloads:
            variance += (workload - mean) ** 2
        imbalance = variance ** 0.5
        self.workloads = workloads
        self.workloads.append(0)

        return (misplaced, time_penalty_value, imbalance)

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

    def new_gene(self, dna=None):
        if dna is None:
            dna = list(random.sample(range(self.N), self.m))
        return Gene(dna, self.occupied, self.time_penalty, self.tasks, self.flattened)

    def run_once(self, timeout, basetime):
        num_population = 1000
        num_child = 100
        population = [self.new_gene() for _ in range(num_population)]
        iter = 0
        while time.time() - basetime < timeout:
            if population[0].penalty() == population[num_population//2].penalty():
                break
            children = []
            for it in range(num_child):
                ga = random.choice(population)
                gb = random.choice(population)
                new_dna = [0] * self.m
                for i in range(self.m):
                    if random.randint(0, 1) == 0:
                        new_dna[i] = ga.dna[i]
                    else:
                        new_dna[i] = gb.dna[i]
                for i in range(self.m):
                    if random.randint(0, 999) < 5:
                        new_dna[i] = min(self.N - 1, max(0, new_dna[i] + random.randint(-5, 5)))
                children.append(self.new_gene(new_dna))
            population += children
            population.sort(key=lambda x:x.penalty())
            population = population[:num_population]
            iter += 1
        return population[0]


    def solve(self, timeout=30):
        basetime = time.time()
        best_gene = None
        while time.time() - basetime < timeout:
            gene = self.run_once(timeout, basetime)
            print(gene.penalty())
            if best_gene is None or best_gene.penalty() > gene.penalty():
                best_gene = gene
        result = []
        for ind, pos in enumerate(best_gene.dna):
            result.append((pos, self.flattened[ind]))
        misplaced, time_penalty_value, imbalance = best_gene.penalty()
        return misplaced, time_penalty_value, best_gene.workloads, result

class AutoScheduler:
    def __init__(self):
        pass
    def schedule(self, events, tasks, send_text, timeout=30):
        code = random.randint(1000, 9999)
        send_text('요청번호 %d번으로 계산을 시작했어요. 결과가 나오면 바로 전해드릴게요!' % code)
        threading.Thread(target=self.optimize, args=(events, tasks, send_text, code, timeout), daemon=True).start()
    def optimize(self, events, tasks, send_text, code, timeout=30):
        N = 14 * 24 * 2
        #N = 1 * 12 * 2
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
            if stamps[N-1] + timedelta(0, 1800) <= start:
                break
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
            if 0 <= stamps[i].hour < 7:
                penalty[i] = 5
            elif 7 <= stamps[i].hour < 10:
                penalty[i] = 1
            elif 22 <= stamps[i].hour:
                penalty[i] = 1

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

        misplaced, time_penalty_value, workloads, solution = self.solve_GA(occupied, penalty, tasks, timeout)
        workloads = list(map(lambda x:x/2, workloads))
        print(workloads)
        average_worktime = sum(workloads) / len(workloads)
        overworks = len(list(filter(lambda x:x>10, workloads)))

        dropout = []
        for pos, ind in solution:
            task = tasks[ind]
            if pos == -1:
                dropout.append(task)
                continue
            dura = task['duration_index']
            result.append((stamps[pos], stamps[pos+dura], task['title']))

        send_text('%d번 계산 결과가 도착했어요!\n- 평균 활동 시간은 %.1f시간이에요.\n- 10시간 초과로 활동하는 날이 %d일 있어요.\n- 야간 활동 패널티는 %d점이에요.' % (code, average_worktime, overworks, time_penalty_value))
        if len(dropout) > 0:
            send_text('다음의 활동이 누락되었어요.\n' + '\n'.join(['- %s (%.1f시간)' % (t['title'], t['duration']) for t in dropout]))
        
        result.sort()
        if len(result) == 0:
            return
        initial_date = result[0][0].date()
        prev_date = result[0][0].date() - timedelta(1)
        message = []
        for start, end, title in result:
            if prev_date < start.date():
                dayname = ['월', '화', '수', '목', '금', '토', '일']
                message.append('')
                message.append('<%d월 %d일 %s요일>' % (start.month, start.day, dayname[start.weekday()]))
                print((start.date()-initial_date).days)
                print(start, end, title)
                worktime = workloads[(start.date() - initial_date).days]
                message.append('• 총 %d시간%s의 활동%s' % (int(worktime), ' 반' if worktime % 1 > 0 else '', '' if worktime <= 10 else '❗'))
                prev_date = start.date()
            message.append('%02d:%02d~%02d:%02d : %s' % (start.hour, start.minute, end.hour, end.minute, title))
        send_text('\n'.join(message))
    
    def solve_GA(self, occupied, penalty, tasks, timeout):
        ga = GA(occupied, penalty, tasks)
        return ga.solve(timeout)

