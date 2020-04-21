# -*- coding: utf-8 -*-
import csv, re

def rid_space(word):
    beg = 0
    end = 0
    beg_stop = False
    end_stop = False
    for idx in range(int(len(word)/2)):
        if word[idx] == ' 'and not beg_stop:
            beg += 1
        else:
            beg_stop = True
        if word[-(idx+1)] == ' ' and not end_stop:
            end -= 1
        else:
            end_stop = True
    
    if end == 0: return word[beg:]
    else: return word[beg:end]
    
def sep_words(s):
    res = list()
    s = re.sub('[=]', ',', s)
    s = s.split(',')
    for w in s:
        res.append(rid_space(w))
    # print("sep_words : ", res)
    return res

def polish_words(word):
    
    res = dict()
    w1 = re.sub('[)]', '', word) # get rid of parenthesis
    w1 = re.sub('[(]', ',', w1) # get rid of parenthesis
    w1 = re.sub('[↔]', '<->', w1)
    
    w1 = w1.split('<->')
    if len(w1) > 1: cand_ant = w1[1]
    else: cand_ant = None
    cand_syn = w1[0]

    if cand_ant: res['antonyms'] = sep_words(cand_ant)
    else: res['antonyms'] = list()
    cand_syn = sep_words(cand_syn)
    res['word'] = cand_syn[0]
    res['synonyms'] = cand_syn[1:]

    return res
    
class CSVParser():
    def __init__(self, path):
        try:
            self.file = open(path, newline = '', encoding='utf-8')
            self.reader = csv.reader(self.file, delimiter = ',')

        except Exception as e:
            print("[ERROR | CSVParser/__init__] {}".format(str(e)))

    def process_file(self):
        res = dict()
        for row in self.reader:
            if len(row) > 0:
                if len(row) > 1:
                    d_wds = polish_words(row[1])
                    extra_info = ','.join(row[2:])
                    v_impf = row[0]
                else:
                    d_wds = polish_words(row[0])
                    extra_info = ''
                    v_impf = 4.0

            res[d_wds['word']] = [v_impf, extra_info]
            for wd in d_wds['synonyms']:
                res[wd] = [v_impf, extra_info]
            for wd in d_wds['antonyms']:
                res[wd] = [v_impf, "ANTONYM OF THE FOLLOWING: " + extra_info]

        return res



if __name__ == '__main__':
    cps = CSVParser('./words_gre4.csv')
    res_process = cps.process_file()
    for r in res_process.keys():
        print("{} : {}".format(r, res_process[r]))
