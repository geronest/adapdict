# -*- coding: utf-8 -*-
from infos.addb import *
from parsers.GetWordProcess import GetWordProcess
from parsers.CSVParser import CSVParser
import multiprocessing as mp
import pickle as pkl
import time


def prepare_words(cw, iw):
    assert len(cand_words) == len(impf_words)
    res = dict()
    for i in range(len(cand_words)):
        res[cand_words[i]] = impf_words[i]

    return res

def save_wordsfailed(path, wf):
    try:
        f_save = open(path, 'w')
        for w in wf: f_save.write('{}\n'.format(w))
        f_save.close()
    except Exception as e:
        print("[ERROR | main/save_wordsfailed] {}".format(str(e)))

path_csv = './csvs/words_gre.csv'
path_sname = 'wgre2'
path_addb = './dbs/{}.addb'.format(path_sname)
path_wf = './{}.wf'.format(path_sname)
num_gwp = 1

if __name__ == '__main__':
    addb = load_addb(path_addb)
    if not addb: addb = AdapDictDB()

    iqueue = mp.Queue(maxsize=3000)
    oqueue = mp.Queue(maxsize=3000)
    mlock = mp.Lock()

    time_parsecsv = time.time()
    csvparser = CSVParser(path_csv)
    cands_word = csvparser.process_file()
    time_parsecsv = time.time() - time_parsecsv
    print("{:.3f} seconds passed for parsing {} words from {}".format(time_parsecsv, len(cands_word), path_csv))
    
    parsers = list()
    for i in range(num_gwp): parsers.append(GetWordProcess(mlock, iqueue, oqueue))
    for i in range(num_gwp): parsers[i].start()
        
    time_getwords = time.time()

    words_in_addb = addb.words.keys()
    words_failed = list()
    
    num_finished_words = 0
    num_test = 0
    num_twords = len(cands_word.keys())
    num_to_print = max(int(num_twords / 50), 1)
    num_words_per_iteration = 100

    cws = list(cands_word.keys())

    num_finished = 0
    while num_finished < num_gwp:

        if len(cws) > 0 and oqueue.qsize() < num_words_per_iteration:
            for cw in cws[:num_words_per_iteration]:
                iqueue.put(cw)
                # cws.remove(cw)
                time.sleep(0.001)
            cws = cws[num_words_per_iteration:]
        
        if len(cws) == 0 and iqueue.qsize() == 0:
            for i in range(len(parsers)):
                iqueue.put('FINISHED')

        if oqueue.qsize() > 0:
            # num_words_got = 0
            rw = oqueue.get()
            if rw:
                if isinstance(rw, list) and rw[0] == 'FINISHED': 
                    num_finished += 1
                    words_failed += rw[1]
                else: 
                    try:
                        if not addb.add_word(rw): 
                            if rw.name not in cands_word.keys():
                                addb.words[rw.name].set_impf(4)
                                num_twords += 1
                            else:
                                addb.words[rw.name].set_impf(cands_word[rw.name][0])
                                addb.words[rw.name].add_smean(cands_word[rw.name][1])
                            # print("new word {} added with impf {}".format(rw.name, addb.words[rw.name].get_impf()))
                            num_finished_words += 1
                            # rw.print_part()
                        else:
                            print("{} is already in addb?".format(rw.name))
                            
                    except Exception as e:
                        print("[ERROR | __main__/quering loop] {}".format(str(e)))

                    # num_words_got += 1
                    if num_finished_words % num_to_print == 0:
                        print("num_finished_words : {:5d} / {:5d} ({:.2f}%)".format(num_finished_words, num_twords, num_finished_words/num_twords * 100))
                        
        else: time.sleep(0.05)
        # time.sleep(0.05)
 
    time_getwords = time.time() - time_getwords

    print("\n\n\n{:.3f} seconds passed for retrieving {} words".format(time_getwords, num_twords))
    print("words_failed: {}".format(words_failed))

    save_addb(addb, path_addb)
    save_wordsfailed(path_wf, words_failed)
    print("\n")

    
    for cw in cands_word:
        if cw not in addb.words.keys():
            print("\"{}\" is not in addb!".format(cw))


    # sw1 = addb.select_words()
    # addb.view_part(sw1)

    #addb.viewl_all(sw1)
    #addb.view_all()
    addb.view_words()
    
