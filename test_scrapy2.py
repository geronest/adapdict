# from scrapy.selector import Selector
# from scrapy.http import Request
import requests
from html.parser import HTMLParser
from html.entities import name2codepoint

class LexicoHTMLParser(HTMLParser):

    def __init__(self):
        super(LexicoHTMLParser, self).__init__()
        self.tags = list()
        self.attrss = list()
        self.print_data = False

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
            if self.tags[-1] == 'span' and ('class', 'ind') in self.attrss[-1]:
                if self.chk_inside('li', ('class', 'subSense')):
                    print("Subsense     :", data)
                else:
                    print("Mainsense    :", data)
            elif self.tags[-1] == 'em' and self.chk_inside('ul', ('class', 'english-ex')):
                print("Example     :", data)


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
    parser = LexicoHTMLParser()
    r = requests.get('https://www.lexico.com/definition/blatant')
    parser.feed(str(r.content))
    # print(r.content)
