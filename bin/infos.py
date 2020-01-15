import numpy as np

class MeanInfo():
    def __init__(self, mean):
        self.mean = mean
        self.exs = list()
        self.subs = list()

    def add_ex(self, ex):
        self.exs.append(ex)

    def add_sub(self, sub):
        self.subs.append(MeanInfo(sub))

    def print_mean(self, num_mean, indent = "  "):
        print(indent + "[Meaning {}: {}]".format(num_mean, self.mean))

    def print_ex(self, num_ex, indent = "  "):
        print(indent + "  ex {}: {}".format(num_ex, self.exs[num_ex]))

    def print_part(self, idx_mean, num_subs = 3, num_exs = 3, indent = "  "):
        self.print_mean(idx_mean, indent)
        ne = min(num_exs, len(self.exs))
        idx_sele = np.random.choice(len(self.exs), ne, replace = False)
        for ise in idx_sele:
            self.print_ex(ise, indent)
        
        ns = min(num_subs, len(self.subs))
        idx_sels = np.random.choice(len(self.subs), ns, replace = False)
        for iss in idx_sels:
            self.subs[iss].print_part(iss, num_subs, num_exs, indent + "  ")

    def print_all(self, num_mean = '1', indent = "  "):
        self.print_mean(num_mean)
        for idx_ex in range(len(self.exs)):
            print(indent + "  ex {}: {}".format(idx_ex+1, self.exs[idx_ex]))
        for idx_sub in range(len(self.subs)):
            self.subs[idx_sub].print_all(indent = indent + "  ", num_mean = '{}-{}'.format(num_mean, idx_sub+1))

class WordInfo():
    def __init__(self, name, impfactor = 1.):
        self.name = name
        self.pos = list()
        self.means = list()
        self.viewnum = 0
        self.impfactor = 1.

    def add_pos(self, pos):
        self.pos.append(pos)
        self.means.append(list())

    def add_mean(self, mean):
        self.means[-1].append(MeanInfo(mean))

    def print_name(self):
        print("[Word : {} (importance factor {})]".format(self.name, self.impfactor))

    def print_pos(self, idx_pos):
        print("  [{}-{}]".format(self.name, self.pos[idx_pos]))

    def print_part(self, num_means = 3, num_subs = 3, num_exs = 3):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            wdm = self.means[idx_pos]
            nm = min(num_means, len(wdm))
            idx_selm = np.random.choice(len(wdm), nm, replace=False)

            for ism in idx_selm:
                wdm[ism].print_part(ism, num_subs, num_exs)

    def print_all(self):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            for idx_mean in range(len(self.means[idx_pos])):
                self.means[idx_pos][idx_mean].print_all(num_mean = idx_mean+1, indent = "  ")

    def view_this(self):
        self.viewnum += 1
        self.impfactor += 1
    
    def half_impf(self):
        self.impfactor /= 2
    
    def set_impf(self, v):
        try:
            self.impfactor = float(v)
        except Exception as e:
            print(str(e))
            print("ERROR: non-float value {} into \'{}\'.impfactor?".format(v, self.name))