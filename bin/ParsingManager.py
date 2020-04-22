# -*- coding: utf-8 -*-
from infos.addb import *
from parsers.GetWordProcess import GetWordProcess
from parsers.CSVParser import CSVParser
import multiprocessing as mp
import pickle as pkl
import time

class ParsingManager():
    def __init__(self, addb, path_addb, name_addb, num_gwp = 1):
        self.iqueue = mp.Queue(maxsize=3000)
        self.oqueue = mp.Queue(maxsize=3000)
        self.mlock = mp.Lock()
        self.addb = addb
        self.path_addb = path_addb
        self.path_wf = './{}.wf'.format(name_addb)
        self.num_gwp = 1

    def save_wordsfailed(self, path, wf):
        try:
            f_save = open(path, 'w')
            for w in wf: f_save.write('{}\n'.format(w))
            f_save.close()
        except Exception as e:
            print("[ERROR | main/save_wordsfailed] {}".format(str(e)))

    def parse_word(self, w, t_wait = 10):
        self.iqueue.put(w)
        gwp = GetWordProcess(self.mlock, self.iqueue, self.oqueue)
        gwp.start()

        words_failed = list()
        t_parse = time.time()
        res = False

        while time.time() - t_parse < t_wait:
            if self.oqueue.qsize() > 0:
                rw = self.oqueue.get()
                if rw:
                    if isinstance(rw, list) and rw[0] == 'FINISHED': 
                        words_failed += rw[1]
                    else: 
                        try:
                            if not self.addb.add_word(rw): 
                                self.addb.words[rw.name].set_impf(4)
                                res = True
                            else:
                                print("{} is already in addb?".format(rw.name))
                                
                        except Exception as e:
                            print("[ERROR | ParsingManager/parse_word] {}".format(str(e)))

            time.sleep(0.1)

        gwp.terminate()
        gwp.join()

        return res

    def parse_csv(self, name_csv = 'default'):
        path_csv = './csvs/{}.csv'.format(name_csv)
        time_parsecsv = time.time()
        csvparser = CSVParser(path_csv)
        cands_word = csvparser.process_file()
        time_parsecsv = time.time() - time_parsecsv
        print("{:.3f} seconds passed for parsing {} words from {}".format(time_parsecsv, len(cands_word), path_csv))
        
        parsers = list()
        for i in range(self.num_gwp): parsers.append(GetWordProcess(self.mlock, self.iqueue, self.oqueue))
        for i in range(self.num_gwp): parsers[i].start()
            
        time_getwords = time.time()

        words_failed = list()
        
        num_finished_words = 0
        num_test = 0
        num_twords = len(cands_word.keys())
        num_to_print = max(int(num_twords / 50), 1)
        num_words_per_iteration = 100

        cws = list(cands_word.keys())

        num_finished = 0
        while num_finished < self.num_gwp:

            if len(cws) > 0 and self.oqueue.qsize() < num_words_per_iteration:
                for cw in cws[:num_words_per_iteration]:
                    if not self.addb.exist_word(cw): self.iqueue.put(cw)
                    # cws.remove(cw)
                    time.sleep(0.001)
                cws = cws[num_words_per_iteration:]
            
            if len(cws) == 0 and self.iqueue.qsize() == 0:
                for i in range(len(parsers)):
                    self.iqueue.put('FINISHED')

            if self.oqueue.qsize() > 0:
                # num_words_got = 0
                rw = self.oqueue.get()
                if rw:
                    if isinstance(rw, list) and rw[0] == 'FINISHED': 
                        num_finished += 1
                        words_failed += rw[1]
                    else: 
                        try:
                            if not self.addb.add_word(rw): 
                                if rw.name not in cands_word.keys():
                                    self.addb.words[rw.name].set_impf(4)
                                    num_twords += 1
                                else:
                                    self.addb.words[rw.name].set_impf(cands_word[rw.name][0])
                                    self.addb.words[rw.name].add_smean(cands_word[rw.name][1])
                                # print("new word {} added with impf {}".format(rw.name, addb.words[rw.name].get_impf()))
                                num_finished_words += 1
                                # rw.print_part()
                            else:
                                print("{} is already in addb?".format(rw.name))
                                
                        except Exception as e:
                            print("[ERROR | ParsingManager/parse_csv] {}".format(str(e)))

                        if num_finished_words % num_to_print == 0:
                            print("num_finished_words : {:5d} / {:5d} ({:.2f}%)".format(num_finished_words, num_twords, num_finished_words/num_twords * 100))
                            
            else: time.sleep(0.05)
    
        for i in range(self.num_gwp): 
            parsers[i].terminate()
            parsers[i].join()

        time_getwords = time.time() - time_getwords

        print("\n\n\n{:.3f} seconds passed for retrieving {} words".format(time_getwords, num_twords))
        print("words_failed: {}".format(words_failed))

        save_addb(self.addb, self.path_addb)
        save_wordsfailed(self.path_wf, words_failed)
        print("\n")
        
        for cw in cands_word:
            if cw not in self.addb.words.keys():
                print("\"{}\" is not in addb!".format(cw))

        # self.addb.view_words()
        
