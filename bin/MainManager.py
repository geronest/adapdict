# -*- coding: utf-8 -*-

from infos.stmn import *
from infos.addb import AdapDictDB, load_addb, save_addb
from quizzers.quizzer import Quizzer
from bin.ParsingManager import ParsingManager

class MainManager():
    def __init__(self, name_addb = 'default'):
        self.path_addb = './dbs/{}.addb'.format(name_addb)
        self.addb = load_addb(self.path_addb)
        if not self.addb: self.addb = AdapDictDB()

        self.pm = ParsingManager(self.addb, self.path_addb, name_addb)
        self.quizzer = Quizzer(self.addb, self.path_addb)
        self.num_run_quiz = 0
        self.num_words_seen = 0
        self.num_words_added = 0

    def mainloop(self):
        while True:

            s_ipt =  s_yellow(s_bold("\n### AdapDict ###\n")) + \
                    "{} words in DB, {} words added | {} quizzes run, {} words viewed\n".format(s_green(str(len(self.addb.words.keys()))), s_green(str(self.num_words_added)), s_green(str(self.num_run_quiz)), s_green(str(self.num_words_seen)) ) + \
                    s_yellow("############\n\n") + \
                    "what do you want to do?\n" + \
                    "  \"{}\": adaptive word quiz\n".format(s_green("quiz")) + \
                    "  \"{}\": search or add a single WORD in the DB. put \'_\' instead of space for WORD like \'see_about\'.\n".format(s_green("find WORD"))  + \
                    "  \"{}\": add words in the csvs/NAME_CSV in the DB. you can skip including \'.csv\'.\n".format(s_green("add NAME_CSV"))  + \
                    "  \"{}\": quit. will save the changes made automatically\n".format(s_green("quit")) + \
                    "\nyour input: "

            ipt = input(s_ipt)
            print("")

            ipt_split = ipt.split(' ')
            if ipt_split[0] == 'quiz':
                s_ipt_quiz = "options in the form of \"NUM_WORD(5~100) SORT_CRITERION(\'impf\' or \'vn\') SELECTION(\'sort\' or \'sample\')\"\n"  + \
                             "(default: 10 impf sample) : "
                opt0 = input(s_ipt_quiz)
                try:
                    opt0_split = opt0.split(' ')
                    n_wds = int(opt0_split[0])
                    if n_wds > 4 and n_wds < 101: opt1 = [n_wds]
                    else: opt1.append(10)
                    if opt0_split[1] in ['impf', 'vn']: opt1.append(opt0_split[1])
                    else: opt1.append('impf')
                    if opt0_split[2] in ['sort', 'sample']: opt1.append(opt0_split[2])
                    else: opt1.append('sample')
                except:
                    print("set to default option, \'10 impf sample\'")
                    opt1 = [10, 'impf', 'sample']
                try:
                    self.quizzer.quiz_sample(opt1[0], opt1[1], opt1[2])
                    self.num_run_quiz += 1
                except:
                    print(s_yellow("\nthere was an error trying to prepare quiz!\n") + "try checking if the DB is empty: {} words".format(len(self.addb.words.keys())))
                    input("enter anything to continue")

            elif ipt_split[0] == 'find':
                try:
                    print("will try to find {}".format(s_yellow(ipt_split[1])))
                    w_to_find = ipt_split[1].replace('_', ' ')
                    if self.addb.exist_word(w_to_find):
                        self.addb.words[w_to_find].print_part(show_mean = True, num_means = -1)
                        self.addb.words[w_to_find].view_this(True)
                        self.num_words_seen += 1
                    else:
                        print("finding {} failed, below are the search results in the DB".format(s_yellow(ipt_split[1])))
                        res_search = self.addb.search_word(ipt_split[1])
                        for w in res_search:
                            print("  " + s_yellow(w))
                        
                        while True:
                            chk_add = input("would you like to get data for {} from the internet? (y/n): ".format(s_yellow(ipt_split[1])))
                            if chk_add == 'y':
                                print("\ntrying to add {} to DB...".format(s_yellow(ipt_split[1])))
                                res_pw = self.pm.parse_word(ipt_split[1])
                                if res_pw[0] > 0:
                                    print("succeeded to add {} to DB".format(s_yellow(str(res_pw[1]))))
                                    self.num_words_added += 1
                                else: 
                                    print(s_red("failed") + " to add {} to DB".format(s_yellow(ipt_split[1])))
                                break

                            elif chk_add == 'n':
                                break

                    input("enter anything to continue")

                except Exception as e:
                    print(e)
                    input("EXCEPTION, try again! (enter anything to continue)")

            elif ipt_split[0] == 'add':
                try:
                    self.num_words_added += self.pm.parse_csv(ipt_split[1])

                    input("enter anything to continue")

                except Exception as e:
                    print(e)
                    input("EXCEPTION, try again! (enter anything to continue)")

            elif ipt_split[0] == 'quit':
                self.quizzer.update_addb()
                print("bye!")
                break

if __name__ == '__main__':

    mm = MainManager('words_gre_5')
    mm.mainloop()
