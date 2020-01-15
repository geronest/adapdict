from fddb import FreqDictDB
from GetWordProcess import GetWordProcess
import multiprocessing as mp
import pickle as pkl
import time

cand_words = ['fast', 'blatant', 'apple', 'dictionary', 'fall', 'acute']
impf_words = [1, 5, 7, 1, 3, 5]

def prepare_words(cw, iw):
    assert len(cand_words) == len(impf_words)
    res = dict()
    for i in range(len(cand_words)):
        res[cand_words[i]] = impf_words[i]

    return res


num_gwp = 8
if __name__ == '__main__':
    fddb = FreqDictDB()
    iqueue = mp.Queue(maxsize=2000)
    oqueue = mp.Queue(maxsize=2000)

    dwords = prepare_words(cand_words, impf_words)

    parsers = list()
    for i in range(num_gwp): parsers.append(GetWordProcess(iqueue, oqueue))
    for i in range(num_gwp): 
        parsers[i].start()
        
    time_getwords = time.time()

    for cw in cand_words:
        iqueue.put(cw)

    while len(fddb.words.keys()) < len(cand_words):
        rw = oqueue.get()
        fddb.add_word(rw)
        fddb.words[rw.name].set_impf(dwords[rw.name])

    for i in range(len(parsers)):
        iqueue.put('FINISHED')

    time_getwords = time.time() - time_getwords

    print("{:.3f} seconds passed for retrieving {} words".format(time_getwords, len(cand_words)))

    name_file = "./sample1.fddb"
    pkl.dump(fddb, open(name_file, 'wb'))
    fddb2 = pkl.load(open(name_file, 'rb'))

    sw1 = fddb2.select_words()
    fddb2.view_part(sw1)

    #fddb.viewl_all(sw1)
    #fddb.view_all()
    # print(r.content)
