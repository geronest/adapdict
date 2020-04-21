# -*- coding: utf-8 -*-
import quizzers.quizzer as qz
from infos.addb import AdapDictDB, load_addb, save_addb
from infos.infos import WordInfo, MeanInfo

if __name__ == '__main__':
    path_addb = './dbs/ph0_copy.addb'
    addb = load_addb(path_addb)
    qz = qz.Quizzer(addb, path_addb)

    qz.quiz_sample(method = 'sample')

