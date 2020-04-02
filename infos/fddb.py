# -*- coding: utf-8 -*-
import random
import numpy as np
import pickle as pkl
from infos import MeanInfo, WordInfo

class FreqDictDB():
    def __init__(self):
        self.words = dict()
        self.criteria_sel = ['impf', 'vn', 'random']
        self.methods_sel = ['sort', 'sample']
    
    def add_word(self, word):
        try:
            if word.name in self.words.keys():
                num_newmeans = 0
                t_wd = self.words[word.name]
                for pos in word.pos:
                    if pos in t_wd.pos:
                        idx_pos = t_wd.pos.index(pos)
                        t_ms = t_wd.means[idx_pos]
                        t_msm = [x.mean for x in t_ms]
                        for mi in word.means[word.pos.index(pos)]:
                            if mi.mean not in t_msm: 
                                t_wd.add_mean(mi, idx_pos)
                                num_newmeans += 1
                    else:
                        t_wd.add_pos(pos)
                        for mi in word.means[word.pos.index(pos)]:
                            t_wd.add_mean(mi)
                            num_newmeans += 1
                # print("FreqDictDB/add_word: {} already existed. {} new meanings added".format(word.name, num_newmeans))    
                return True # Already existed
            else:
                self.words[word.name] = word
                return False
        except Exception as e:
            print("[ERROR | FreqDictDB/add_word()] {}, {}".format(word, str(e)))

    def exist_word(self, w):
        res = w in self.words.keys()
        return res

    def search_word(self, s): # s could be a substring of the target word(s)
        res = list()
        for w in list(self.words.keys()):
            if s in w: res.append(w)
        return res
    
    def view_word(self, word):
        curr_word = self.words[word]
        curr_word.print_all()
        curr_word.view_this()
        print("")

    def view_part(self, l, num_words = 3, num_means = 3, num_subs = 3, num_exs = 3):
        nw = min(num_words, len(l))
        idx_selw = np.sort(np.random.choice(len(l), nw, replace=False))
        lw = [l[i] for i in idx_selw]

        for wd in lw:
            wd.print_part(num_means, num_subs, num_exs)
            print("")
    
    def view_all(self):
        for word in self.words.keys():
            self.view_word(word)
    
    def view_words(self):
        for word in self.words.keys():
            print(word)

    def viewl_all(self, l):
        for word in l:
            print("{}.viewnum: {}".format(word.name, self.words[word.name].viewnum))
            word.print_all()
            word.view_this()
            print("{}.viewnum: {}".format(word.name, self.words[word.name].viewnum))
            print("")
        
    def select_words(self, num_words = 10, criterion = 'impf', method = 'sort'):
        assert criterion in self.criteria_sel
        assert method in self.methods_sel

        len_words = len(self.words.keys())
        num_words = min(num_words, len_words)
        cand_words = list(self.words.values())

        if criterion == 'impf':
            if method == 'sort':
                sorted_words = sorted(cand_words, key=lambda x: x.impfactor, reverse = True)
                return sorted_words[:num_words]

            elif method == 'sample':
                impfs = np.array([x.impfactor for x in cand_words])
                impfs_norm = impfs / np.sum(impfs)
                idx_sel = np.random.choice(len_words, num_words, p = impfs_norm, replace = False)
                return [cand_words[i] for i in idx_sel]

        elif criterion == 'vn':
            if method == 'sort':
                sorted_words = sorted(cand_words, key=lambda x: x.viewnum, reverse = True)
                return sorted_words[:num_words]
            elif method == 'sample':
                vns = np.array([x.viewnum for x in cand_words])
                vns_norm = vns / np.sum(vns)
                idx_sel = np.random.choice(len_words, num_words, p = vns_norm, replace = False)
                return [cand_words[i] for i in idx_sel]

        elif criterion == 'random':
            res = list()
            idxs = list(range(num_words))
            random.shuffle(idxs)
            for i in range(num_words):
                res.append(cand_words[idxs[i]])

            return res



if __name__ == '__main__':
    def load_fddb(path):
        res = None
        try:
            res = pkl.load(open(path, 'rb'))
            print("main/load_fddb: successfully loaded {}, {} words".format(path, len(res.words.keys())))
        except Exception as e:
            print("[ERROR | main/load_fddb] {}".format(str(e)))
        return res
    path_fddb = './test_check.fddb'
    fddb = load_fddb(path_fddb)
    #fddb.view_word('record')
    #print(fddb.search_word('serendip'))
    fddb.view_all()
    fddb.view_words()