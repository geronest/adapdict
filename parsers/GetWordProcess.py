import multiprocessing as mp
import requests_html, time, random
from parsers.LexicoHTMLParser import LexicoHTMLParser

class GetWordProcess(mp.Process):
    def __init__(self, mlock, iqueue, oqueue):
        super(GetWordProcess, self).__init__()
        self.lock = mlock
        self.iqueue = iqueue
        self.oqueue = oqueue
        self.lhp = LexicoHTMLParser()
        self.words_to_get = list()
        self.sess = requests_html.HTMLSession()
        self.max_retry = 3
        self.max_sleep = 3
        self.t_sleep = 20

        self.words_failed = dict()
        self.words_collected = list()
        #print("GWP init complete")

    def run(self):
        #print("GWP running")
        finished_iqueue = False
        while True:
            try:
                # print("GWP while 0")
                if not finished_iqueue:
                    self.lock.acquire()
                    out_iqueue = self.iqueue.get()
                    self.lock.release()
                    if out_iqueue == 'FINISHED': finished_iqueue = True
                    else: target = out_iqueue

                if finished_iqueue:
                    if len(self.words_to_get) == 0:
                        self.oqueue.put(['FINISHED', list(self.words_failed.keys())])
                        break
                    else: 
                        random.shuffle(self.words_to_get)
                        # print("\n\nself.words_to_get: {}".format(self.words_to_get))
                        target = self.words_to_get.pop(0)
                        # print("trying word {}\n\n".format(target))
                
                if target in self.words_collected: 
                    print("[GWP] target \'{}\' already exists in fddb. skipping".format(target))
                    continue

                target = target.replace(' ', '_')
                url_target = 'https://www.lexico.com/en/definition/{}'.format(target)
            
                retry = False
                try:
                    r = self.sess.get(url_target)
                    if r.url != url_target and 'search?filter' in r.url:
                        r.html.render()
                        content = str(r.html.html)
                    else:
                        content = str(r.content)

                    self.lhp.reset_words()
                    try:
                        self.lhp.feed(str(content))
                    except Exception as e:
                        print("GWP({}: lhp.feed): ".format(target), str(e))

                    words, additional_words = self.lhp.get_wordinfo()

                    # print("\n\nwords, additional words for {}: {}, {}\n\n".format(target, words, additional_words))
                    # print("\n\n")
                    self.words_to_get += additional_words
                    
                    # if additional_words: print("words_to_get: {}".format(self.words_to_get))
                    if not words: 
                        print("[ERROR] target {} not parsed from HTMLParser, maybe not found in lexico.com.".format(target))
                        retry = True
                    else:
                        for w in words: 
                            self.oqueue.put(w)
                            self.words_collected.append(w.name)
                            if w == target:
                                if retry: print("\n\nword {} is not going to be retried!\n\n".format(target))
                                retry = False
                                
                            if w in self.words_failed.keys(): 
                                del self.words_failed[w]

                except Exception as e:
                    print("GWP({}: get,render): ".format(target), str(e))
                    retry = True
                    
                if retry: 
                    if target in self.words_failed:
                        self.words_failed[target] += 1
                    else: 
                        self.words_failed[target] = 0
                        
                    # total_sleep = self.t_sleep * (2 ** self.words_failed[target])
                    total_sleep = self.t_sleep
                    time.sleep(total_sleep)
                    if self.words_failed[target] < self.max_retry: self.words_to_get.append(target)
                    print("[GWP-RETRY {}: {}] slept for {} seconds".format(target, self.words_failed[target], total_sleep))
                    
                            
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                print("KeyboardInterrupt, SystemExit")
                break
            except Exception as e:
                print("GWP: ", str(e))


            


