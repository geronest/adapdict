# from scrapy.selector import Selector
# from scrapy.http import Request
import requests, random, time
import pickle as pkl
import numpy as np
from html.parser import HTMLParser
from html.entities import name2codepoint


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

    def print_part(self, idx_mean, num_subs = 3, num_exs = 3):
        self.print_mean(idx_mean)
        ne = min(num_exs, len(self.exs))
        idx_sele = np.random.choice(len(self.exs), ne, replace = False)
        for ise in idx_sele:
            self.print_ex(ise)
        
        ns = min(num_subs, len(self.subs))
        idx_sels = np.random.choice(len(self.subs), ns, replace = False)
        for iss in idx_sels:
            self.subs[iss].print_part(iss, num_subs, num_exs)

    def print_all(self, num_mean = '1', indent = "  "):
        self.print_mean(num_mean)
        for idx_ex in range(len(self.exs)):
            print(indent + "  ex {}: {}".format(idx_ex+1, self.exs[idx_ex]))
        for idx_sub in range(len(self.subs)):
            self.subs[idx_sub].print_all(indent = indent + "  ", num_mean = '{}-{}'.format(num_mean, idx_sub+1))

class WordInfo():
    def __init__(self, name, impfactor = 1.):
        self.name = name
        self.pos = list()
        self.means = list()
        self.viewnum = 0
        self.impfactor = 1.

    def add_pos(self, pos):
        self.pos.append(pos)
        self.means.append(list())

    def add_mean(self, mean):
        self.means[-1].append(MeanInfo(mean))

    def print_name(self):
        print("[Word : {} (importance factor {})]".format(self.name, self.impfactor))

    def print_pos(self, idx_pos):
        print("  [{}-{}]".format(self.name, self.pos[idx_pos]))

    def print_part(self, num_means = 3, num_subs = 3, num_exs = 3):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            wdm = self.means[idx_pos]
            nm = min(num_means, len(wdm))
            idx_selm = np.random.choice(len(wdm), nm, replace=False)

            for ism in idx_selm:
                wdm[ism].print_part(ism, num_subs, num_exs)

    def print_all(self):
        self.print_name()
        for idx_pos in range(len(self.pos)):
            self.print_pos(idx_pos)
            for idx_mean in range(len(self.means[idx_pos])):
                self.means[idx_pos][idx_mean].print_all(num_mean = idx_mean+1, indent = "  ")

    def view_this(self):
        self.viewnum += 1
        self.impfactor += 1
    
    def half_impf(self):
        self.impfactor /= 2
    
    def set_impf(self, v):
        try:
            self.impfactor = float(v)
        except Exception as e:
            print(str(e))
            print("ERROR: non-float value {} into \'{}\'.impfactor?".format(v, self.name))


class FreqDictDB():
    def __init__(self):
        self.words = dict()
        self.criteria_sel = ['impf', 'vn', 'random']
        self.methods_sel = ['sort', 'sample']
    
    def add_word(self, word):
        self.words[word] = WordInfo(word)

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
    
    def view_all(self):
        for word in self.words.keys():
            self.view_word(word)

    def viewl_all(self, l):
        for word in l:
            print("{}.viewnum: {}".format(word.name, self.words[word.name].viewnum))
            word.print_all()
            word.view_this()
            print("{}.viewnum: {}".format(word.name, self.words[word.name].viewnum))
            print("")
        


    # criterion = {'impf', 'vn', 'random'}
    # method = {'sort', 'sample'}
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

class LexicoHTMLParser(HTMLParser):

    def __init__(self, fddb):
        super(LexicoHTMLParser, self).__init__()
        self.tags = list()
        self.attrss = list()
        self.fddb = fddb
        self.print_data = False
        self.curr_word = ""

    def chk_inside(self, tag, attr):
        for i in range(len(self.tags)):
            if tag == self.tags[-(i+1)] and attr in self.attrss[-(i+1)]:
                return True
        return False
                
    def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag)

        self.tags.append(tag)
        self.attrss.append(attrs)

        assert len(self.tags) == len(self.attrss)

        # print(self.tags, self.attrss)
                

    def handle_endtag(self, tag):
        if tag == self.tags[-1]:
            self.tags.pop(-1)
            self.attrss.pop(-1)
        else:
            print("ERROR: Invalid HTML????")
            raise ValueError

    def handle_data(self, data):
        if len(self.tags) > 0:
            if self.tags[-1] == 'span' and ('class', 'hw') in self.attrss[-1]:
                self.curr_word = data
                self.fddb.add_word(data)
                #self.words.append(WordInfo(data))

            elif self.tags[-1] == 'span' and ('class', 'pos') in self.attrss[-1]:
                self.fddb.words[self.curr_word].add_pos(data)

            elif self.tags[-1] == 'span' and ('class', 'ind') in self.attrss[-1]:
                if self.chk_inside('li', ('class', 'subSense')):
                    self.fddb.words[self.curr_word].means[-1][-1].add_sub(data)
                    #print("Subsense     :", data)
                else:
                    #print("data {}, self.curr_word {}".format(data, self.curr_word) )
                    self.fddb.words[self.curr_word].add_mean(data)
                    
                    
            elif self.tags[-1] == 'em' and self.chk_inside('ul', ('class', 'english-ex')):
                if self.chk_inside('li', ('class', 'subSense')):
                    self.fddb.words[self.curr_word].means[-1][-1].subs[-1].add_ex(data)
                    #self.words[-1].means[-1].subs[-1].add_ex(data)
                else:
                    self.fddb.words[self.curr_word].means[-1][-1].add_ex(data)
                    #self.words[-1].means[-1].add_ex(data)

                #print("Example     :", data)
        
    def handle_comment(self, data):
        pass
        # print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        # print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        # print("Num ent  :", c)

    def handle_decl(self, data):
        pass
        # print("Decl     :", data)



# request = Request(url = 'https://www.lexico.com/definition/blatant')
# print(request)

# res_ind = Selector(response = response)
# print(res_ind)

if __name__ == '__main__':
    fddb = FreqDictDB()
    parser = LexicoHTMLParser(fddb)
    #cand_words = ['fast']
    cand_words = ['fast', 'blatant', 'apple', 'dictionary', 'fall', 'acute']
    impf_words = [1, 5, 7, 1, 3, 5]

    time_getwords = time.time()
    for idx_word in range(len(cand_words)):
        r = requests.get('https://www.lexico.com/definition/{}'.format(cand_words[idx_word]))
        parser.feed(str(r.content))
        fddb.words[parser.curr_word].set_impf(impf_words[idx_word])
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

