# -*- coding: utf-8 -*-
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
        idx_sele = np.sort(np.random.choice(len(self.exs), ne, replace = False))
        for ise in idx_sele:
            self.print_ex(ise, indent)
        
        ns = min(num_subs, len(self.subs))
        idx_sels = np.sort(np.random.choice(len(self.subs), ns, replace = False))
        for iss in idx_sels:
            self.subs[iss].print_part(iss, num_subs, num_exs, indent + "  ")

    def print_all(self, num_mean = '1', indent = "  "):
        self.print_mean(num_mean, indent)
        for idx_ex in range(len(self.exs)):
            print(indent + "  ex {}: {}".format(idx_ex+1, self.exs[idx_ex]))
        for idx_sub in range(len(self.subs)):
            self.subs[idx_sub].print_all(indent = indent + "  ", num_mean = '{}-{}'.format(num_mean, idx_sub+1))

class WordInfo():
    def __init__(self, name, impfactor = 1., num_ts = 5):
        self.name = name
        self.pos = list()
        self.means = list()
        self.smeans = list()
        self.phrases = list()
        self.phrasalverbs = list()
        self.syns = list()
        self.ants = list()
        self.origin = ""

        self.viewnum = 0
        self.impfactor = 1.
        self.nrem = 0
        self.thr_nrem = 3 # threshold of rememberance num. for halving impf
        self.timestamps = list()

    def add_pos(self, pos):
        self.pos.append(pos)
        self.means.append(list())

    def add_mean(self, mean, idx_pos = -1):
        if self.means:
            self.means[idx_pos].append(MeanInfo(mean))
        else:
            print("[WordInfo - \'{}\'] no pos added yet, but a meaning \'{}\' came in. temporarily assigning \'???\' to the latest pos".format(self.name, mean))
            self.add_pos('???')
            self.means[-1].append(MeanInfo(mean))

    def add_phrase(self, phrase):
        self.phrases.append(phrase)

    def add_phrasalverb(self, phrasalverb):
        self.phrasalverbs.append(phrasalverb)

    def add_smean(self, mean):
        self.smeans.append(mean)

    def set_origin(self, origin):
        self.origin += origin

    def print_name(self):
        print("[Word : {} (importance factor {})]".format(self.name, self.impfactor))

    def print_pos(self, idx_pos):
        print("  [{}-{}]".format(self.name, self.pos[idx_pos]))

    def print_ph(self, phs, type_ph = "phrase"):
        if phs:
            res = "  [{}-{}] ".format(self.name, type_ph)
            for idx_ph in range(len(phs)):
                if idx_ph > 0: res += ", "
                res += phs[idx_ph]
            print(res)

    def print_origin(self):
        if len(self.origin):print("  Origin: {}".format(self.origin))
        
    def print_part(self, num_means = 3, num_subs = 3, num_exs = 3):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            wdm = self.means[idx_pos]
            nm = min(num_means, len(wdm))
            idx_selm = np.random.choice(len(wdm), nm, replace=False)

            for ism in idx_selm:
                wdm[ism].print_part(ism, num_subs, num_exs)
        self.print_ph(self.phrases, "phrases")
        self.print_ph(self.phrasalverbs, "phrasal verbs")        
        self.print_origin()

    def print_all(self):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            for idx_mean in range(len(self.means[idx_pos])):
                self.means[idx_pos][idx_mean].print_all(num_mean = idx_mean+1, indent = "  ")
        self.print_ph(self.phrases, "phrases")
        self.print_ph(self.phrasalverbs, "phrasal verbs")
        self.print_origin()

    def view_this(self):
        self.viewnum += 1
        self.impfactor += 1

    def check_rem(self, rem = False):
        if rem:
            self.nrem += 1
            if self.nrem >= self.thr_nrem:
                self.half_impf()
                self.nrem = 0
        else:
            self.nrem = 0
    
    def half_impf(self):
        self.impfactor /= 2

    def get_impf(self):
        return self.impfactor
    
    def set_impf(self, v):
        try:
            self.impfactor = float(v)
        except Exception as e:
            print(str(e))
            print("ERROR: non-float value {} into \'{}\'.impfactor?".format(v, self.name))