class Foo(object):

     def __init__(self, score):
         self.score = score

     def __lt__(self, other):
         return self.score < other.score
     
class Day:
    def __init__(self, job, date, begin, end, pause, worktime):
        self.job = job
        self.date = date
        self.begin = int(begin)
        self.end = int(end)
        self.worktime = int(worktime)
        self.pause = int(pause)

    def __lt__(self, other):
        return self.date < other.date


from datetime import date
d1 = date(2000, 8, 3)
d2 = date(2001, 7, 3)

D1 = Day("Job", d1, 1, 1, 1, 1)
D2 = Day("Job", d2, 1, 1, 1, 1)
print([D1, D2])
print(sorted([D2, D1]))

