from html.parser import HTMLParser
from infos import WordInfo

class LexicoHTMLParser(HTMLParser):

    def __init__(self):
        super(LexicoHTMLParser, self).__init__()
        self.tags = list()
        self.attrss = list()
        self.curr_word = None

    def get_wordinfo(self):
        return self.curr_word

    def chk_inside(self, tag, attr):
        for i in range(len(self.tags)):
            if tag == self.tags[-(i+1)] and attr in self.attrss[-(i+1)]:
                return True
        return False
                
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrss.append(attrs)
        assert len(self.tags) == len(self.attrss)

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
                self.curr_word = WordInfo(data)
                
            elif self.tags[-1] == 'span' and ('class', 'pos') in self.attrss[-1]:
                self.curr_word.add_pos(data)

            elif self.tags[-1] == 'span' and ('class', 'ind') in self.attrss[-1]:
                if self.chk_inside('li', ('class', 'subSense')):
                    self.curr_word.means[-1][-1].add_sub(data)
                else:
                    self.curr_word.add_mean(data)
                    
            elif self.tags[-1] == 'em' and self.chk_inside('ul', ('class', 'english-ex')):
                if self.chk_inside('li', ('class', 'subSense')):
                    self.curr_word.means[-1][-1].subs[-1].add_ex(data)
                else:
                    self.curr_word.means[-1][-1].add_ex(data)
                    
        
