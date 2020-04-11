# -*- coding: utf-8 -*-
import random
import numpy as np
import pickle as pkl
from infos.addb import AdapDictDB, load_addb, save_addb
from infos.infos import MeanInfo, WordInfo

class Quizzer():
    def __init__(self, addb, path_addb):
        self.addb = addb
        self.path_addb = path_addb
        self.kbipts = dict() # keyboard inputs
        self.kbipts['yn'] = ['y', 'n']
        self.kbipts['cm'] = ['q']

    def update_addb(self, words_dkn = None):
        if words_dkn: print("words checked unknown: {}".format(words_dkn))
        save_addb(self.addb, self.path_addb)

    def quiz_sample(self, num_words = 10, criterion = 'impf', method = 'sort'):
        ws = self.addb.select_words(num_words = num_words, criterion = criterion, method = method)
        words_dkn = list()
        quit_quiz = False
        for w in ws:
            # TODO: check if the user knows this word, process accordingly
            print("")
            w.print_part(show_mean = False)
            while True:
                know_word = input("Do you know this word? (Y or y / N or n / Q or q): ")

                if know_word.lower() in self.kbipts['yn'] + self.kbipts['cm']:
                    if know_word.lower() == 'y':
                        w.check_rem(True)
                    elif know_word.lower() == 'n':
                        print("\n### review with meanings ###")
                        w.print_part(show_mean = True, num_means = -1)
                        w.check_rem(False)
                        print("")
                        w.view_this(True)
                        words_dkn.append(w.name)
                        input("enter anything to continue")
                    elif know_word.lower() == 'q':
                        quit_quiz = True
                    break
            
            if quit_quiz: 
                self.update_addb(words_dkn)
                break
        self.update_addb(words_dkn)
            






if __name__ == '__main__':
    path_addb = 'dbs/cd_gre_test.addb'
    addb = load_addb(path_addb)
    qz = Quizzer(addb, path_addb)

    qz.quiz_sample()





