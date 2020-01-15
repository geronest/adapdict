import multiprocessing as mp
import requests, time
from LexicoHTMLParser import LexicoHTMLParser

class GetWordProcess(mp.Process):
    def __init__(self, iqueue, oqueue):
        super(GetWordProcess, self).__init__()
        self.iqueue = iqueue
        self.oqueue = oqueue
        self.lhp = LexicoHTMLParser()
        #print("GWP init complete")

    def run(self):
        #print("GWP running")
        while True:
            try:
                # print("GWP while 0")
                target = self.iqueue.get()
                if target == 'FINISHED':
                    break
                else:
                    r = requests.get('https://www.lexico.com/definition/{}'.format(target))
                    self.lhp.feed(str(r.content))
                    word = self.lhp.get_wordinfo()
                    self.oqueue.put(word)
                time.sleep(0.05)
            except Exception as e:
                print(str(e))


            


