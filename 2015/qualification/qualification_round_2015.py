import sys
from math import pow
import copy
from random import randint

class Server(object):
    def __init__(self, idx, z, c):
        self.idx=idx
        self.size=z
        self.cap=c
        self.group=None
        self.pos=None
        self.black_list = False

    @property
    def score(self):
        return float(self.cap)/pow(self.size, 1.0691)
    
    def place(self, r, c, g):
        self.pos = (r, c)
        self.group = g

def get_servers_by_row_by_group(servers):
    out = {}
    for s in servers:
        if s.group is not None:
            if s.pos[0] not in out:
                out[s.pos[0]] = {}
            if s.group not in out[s.pos[0]]:
                out[s.pos[0]][s.group] = []
            out[s.pos[0]][s.group].append(s)
    return out

def condamn(available_slots, r, c, s=1):
    idx=-1
    d=c+s-1
    for i, (a, b) in enumerate(available_slots[r]):
        if a <= c and b >= d:
            idx=i
            break
    if idx==-1:
        raise ValueError("No condamnable slots")
    a, b = available_slots[r][idx]
    del available_slots[r][idx]
    if a < c:
        available_slots[r].append((a, c-1))
    if b > d:
        available_slots[r].append((d+1, b))
    available_slots[r] = sorted(available_slots[r], key=lambda x: x[0])

def select_group(groups_gcap):
    return groups_gcap.index(min(groups_gcap))

def find_slot(s, r, available_slots):
    n = -1
    candidate = None
    for i, (a, b) in enumerate(available_slots[r]):
        if b-a+1 >= s.size:
            if n == -1 or b-a+1>n:
                n = b-a+1
                candidate=a
    return candidate

def select_pos(s, g, groups_row_cap, available_slots):
    cap_by_row = groups_row_cap[g]
    best_rows = sorted(range(len(cap_by_row)), key=lambda i: cap_by_row[i])
    for r in best_rows:
        c = find_slot(s, r, available_slots)
        if c is not None:
            return r, c
    return None

def insert_in_group(s, r, c, g, groups_cap, groups_row_cap, groups_gcap, available_slots):
    s.place(r, c, g)
    condamn(available_slots, r, c, s.size)
    groups_cap[g] += s.cap
    groups_row_cap[g][r] += s.cap
    compute_gcap(g, groups_gcap, groups_cap, groups_row_cap)

def compute_gcap(g, groups_gcap, groups_cap, groups_row_cap):
    groups_gcap[g] = groups_cap[g] - max(groups_row_cap[g])

def optimize(servers, groups_cap, groups_row_cap, groups_gcap, available_slots):
    for s in servers:
        if s.black_list:
            continue
        g = select_group(groups_gcap)
        pos = select_pos(s, g, groups_row_cap, available_slots)
        if pos is None:
            continue
        r, c = pos
        insert_in_group(s, r, c, g, groups_cap, groups_row_cap, groups_gcap, available_slots)

def find_black_sheeps(servers, score, groups_gcap):
    servers = [s for s in servers if s.group is not None]
    worst_group = groups_gcap.index(score)
    worst_row_for_worst_group = groups_row_cap[worst_group].index(max(groups_row_cap[worst_group]))
    servers_by_row_by_group = get_servers_by_row_by_group(servers)
    worsts = servers_by_row_by_group[worst_row_for_worst_group][worst_group]
    return worsts

def re_init(servers):
    for s in servers:
        s.pos = None
        s.group = None

if __name__ == '__main__':
    file_in = sys.argv[1]
    servers = []
    available_slots=[]
    groups_cap = []
    groups_gcap = []
    groups_row_cap = []
    with open(file_in, "r") as in_file:
        R, S, U, P, M = [int(a) for a in in_file.readline().split(" ")]
        print R, S, U, P, M
        for i in range(R):
            available_slots.append([(0, S-1)])
        for i in range(U):
            r, c = [int(a) for a in in_file.readline().split(" ")]
            condamn(available_slots, r, c)
        for i in range(M):
            z, c = [int(a) for a in in_file.readline().split(" ")]
            servers.append(Server(i, z, c))
        for i in range(P):
            groups_cap.append(0)
            groups_gcap.append(0)
            groups_row_cap.append([0]*R)
    servers = sorted(servers, reverse=True, key=lambda x:x.score)
    optimize(servers, groups_cap, groups_row_cap, groups_gcap, available_slots)  
    score = min(groups_gcap) 
    for i in range(1):
        prev_score = score
        black_sheeps = find_black_sheeps(servers, score, groups_gcap)
        print "there a {0} black sheeps".format(len(black_sheeps))
        r = randint(0, len(black_sheeps)-1)
        bs = black_sheeps[r]
        print bs.idx
        print "trying to remove black sheep {0}".format(bs)
        re_init(servers)
        bs.black_list = True
        available_slots=[]
        groups_cap = []
        groups_gcap = []
        groups_row_cap = []
        for i in range(P):
            groups_cap.append(0)
            groups_gcap.append(0)
            groups_row_cap.append([0]*R)
        for i in range(R):
            available_slots.append([(0, S-1)])
        optimize(servers, groups_cap, groups_row_cap, groups_gcap, available_slots)   
        score = min(groups_gcap)
        if score <= prev_score:
            bs.black_list = False
        else:
            print "better score found {0}".format(score)
    print "final score: {}".format(min(groups_gcap))
    placed = 0
    with open("sol.txt", "w") as outf:
        for s in sorted(servers, key=lambda x:x.idx):
            if s.group is not None:
                outf.write("{} {} {}\n".format(s.pos[0], s.pos[1], s.group))
                placed+=1
            else:
                outf.write("x\n")
    print "{0} servers placed".format(placed)




