from html.parser import HTMLParser
from infos.infos import WordInfo

class LexicoHTMLParser(HTMLParser):

    def __init__(self):
        super(LexicoHTMLParser, self).__init__()
        self.reset_words()
    
    def reset_words(self):
        self.tags = list()
        self.attrss = list()
        self.curr_words = list()
        self.curr_word = None
        self.additional_word = list()
        self.phrase_last = None
        self.tag_last_ph = None
        self.at_origin = False
        self.temp_data = None

    def get_wordinfo(self):
        # if not isinstance(self.curr_word, WordInfo): print("self.curr_word is not WordInfo?? {}".format(self.curr_word))
        return self.curr_words, self.additional_word

    def chk_inside(self, tag, attr):
        try:
            for i in range(len(self.tags)):
                if tag == self.tags[-(i+1)] and attr in self.attrss[-(i+1)]:
                    return True
        except Exception as e:
            print("[ERROR | LHP/chk_inside] {}".format(str(e)))
        return False
                
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrss.append(attrs)
        assert len(self.tags) == len(self.attrss)

    def handle_endtag(self, tag):
        try:
            if tag == 'section' and self.at_origin: self.at_origin = False
            if tag == self.tags[-1]:
                self.tags.pop(-1)
                self.attrss.pop(-1)
        except Exception as e:
            print("HTMLParser/handle_endtag: ERROR {}".format(str(e)))


    def handle_data(self, data):
        if len(self.tags) > 0:
            try:
                if self.tags[-1] == 'span' and ('class', 'hw') in self.attrss[-1]:
                    try:
                        if len(self.curr_words) > 0:
                            self.curr_words.append(WordInfo(data + str(len(self.curr_words))))
                        else:
                            self.curr_words.append(WordInfo(data))
                        self.curr_word = self.curr_words[-1]
                        # print("span-hw-{}".format(data))
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) span-hw-{} {}".format(self.curr_word.name, str(e), data))

                elif self.tags[-1] == 'strong' and self.chk_inside('h3', ('class', 'phrases-title')):
                    try:
                        if data == 'Phrases':
                            self.tag_last_ph = 'phrase'
                        elif data == 'Phrasal Verbs':
                            self.tag_last_ph = 'phrasalverb'
                        # print("strong-phrases_title-{}".format(data))
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) strong-phrases_title-{} {}".format(self.curr_word.name, str(e), data))

                elif self.tags[-1] == 'strong' and ('class', 'phrase') in self.attrss[-1]:
                    try:
                        if self.tag_last_ph == 'phrase':
                            self.curr_word.add_phrase(data)
                        elif self.tag_last_ph == 'phrasalverb':
                            self.curr_word.add_phrasalverb(data)
                        if data not in self.additional_word: 
                            # print("adding {} to additional_word".format(data))
                            # self.additional_word.append(data)
                            pass
                        # print("strong-phrase-{}".format(data))
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) strong-phrase-{} {}".format(self.curr_word.name, str(e), data))

                elif self.tags[-1] == 'a' and ('class', 'no-transition') in self.attrss[-1] and self.chk_inside('span', ('class', 'noad_results')):
                    try:
                        if data not in self.additional_word: self.additional_word.append(data)
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) a-no-transition {}".format(data, str(e)))
                    
                elif self.tags[-1] == 'span' and ('class', 'pos') in self.attrss[-1] and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        self.curr_word.add_pos(data)
                        # print("span-pos-{}".format(data))
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) span-pos-{}".format(self.curr_word.name, str(e)))

                elif self.tags[-1] == 'span' and ('class', 'ind') in self.attrss[-1] and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        if self.chk_inside('li', ('class', 'subSense')):
                            self.curr_word.means[-1][-1].add_sub(data)
                        else:
                            self.curr_word.add_mean(data)
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) span-ind-{}\n{}\n".format(self.curr_word.name, str(e), data))
                        
                elif self.tags[-1] == 'a' and self.chk_inside('p', ('class', 'derivative_of')) and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        if self.chk_inside('li', ('class', 'subSense')):
                            self.curr_word.means[-1][-1].add_sub("See {}".format(data))
                        else:
                            self.curr_word.add_mean("See {}".format(data))
                        if data not in self.additional_word: self.additional_word.append(data)
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) p-derivative_of-a-{}".format(self.curr_word.name, str(e)))

                elif self.tags[-1] == 'div' and ('class', 'crossReference') in self.attrss[-1] and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        if data[0] == "\"" and data[-1] == "\"": data = data[1:-1]
                        self.temp_data = data
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) div-crossReference-{}".format(self.curr_word.name, str(e)))

                elif self.tags[-1] == 'a' and self.chk_inside('div', ('class', 'crossReference')) and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        if self.chk_inside('li', ('class', 'subSense')):
                            self.curr_word.means[-1][-1].add_sub(self.temp_data + data)
                        else:
                            self.curr_word.add_mean(self.temp_data + data)
                        if data not in self.additional_word: self.additional_word.append(data)
                        self.temp_data = None
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) div-crossReference-a-{}".format(data, str(e)))

                elif self.tags[-1] == 'em' and (self.chk_inside('ul', ('class', 'english-ex')) or self.chk_inside('div', ('class', 'ex'))) and self.chk_inside('section', ('class', 'gramb')):
                    try:
                        if self.chk_inside('li', ('class', 'subSense')):
                            self.curr_word.means[-1][-1].subs[-1].add_ex(data)
                        else:
                            self.curr_word.means[-1][-1].add_ex(data)
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) em-english-ex-{}\n{}\n".format(self.curr_word.name, str(e), data))

                # elif data == 'Origin' and self.tags[-1] == 'strong' and self.chk_inside('h3', ()) and self.chk_inside('section', ('class', 'etymology etym')):
                elif data == 'Origin' and self.tags[-1] == 'strong' and self.chk_inside('section', ('class', 'etymology etym')):
                    try:
                        self.at_origin = True
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}) strong-phrase-{} {}".format(self.curr_word.name, str(e), data))

                # elif self.tags[-1] == 'p' and self.chk_inside('section', ('class', 'etymology etym')) and self.at_origin:
                elif self.chk_inside('section', ('class', 'etymology etym')) and self.at_origin:
                    try:
                        self.curr_word.set_origin(data)
                    except Exception as e:
                        print("[ERROR | LHP/handle_data] ({}, Origin) p-{} {}".format(self.curr_word.name, str(e), data))


            except Exception as e:
                print("[ERROR | LHP/handle_data] {}".format(str(e)))
                    
if __name__ == '__main__':
    import requests, requests_html, re
    lhp = LexicoHTMLParser()
    sess = requests_html.HTMLSession()

    cand_words = ['lay-out', 'serendipitiously']
    for wd in cand_words:

        url_orig = 'http://www.lexico.com/en/definition/{}'.format(wd)
        r = sess.get(url_orig)
        if url_orig != r.url and 'search?filter' in r.url:
            print('rendering html')
            r.html.render()
            content = str(r.html.html)
        else:
            content = str(r.content)
        lhp.reset_words()
        lhp.feed(content)
        w, aw = lhp.get_wordinfo()
        if w: print(w.name, w.means[0][0].mean)
        print(aw)
        # print('layout' in str(r2.content))
