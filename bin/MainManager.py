from infos.stmn import *
from infos.addb import AdapDictDB, load_addb, save_addb
from quizzers.quizzer import Quizzer
from ParsingManager import ParsingManager

class MainManager():
    def __init__(self, name_addb = 'default'):
        self.path_addb = './dbs/{}.addb'.format(name_addb)
        self.addb = load_addb(self.path_addb)
        if not self.addb: self.addb = AdapDictDB()

        self.pm = ParsingManager(self.addb, self.path_addb, name_addb)
        self.quizzer = Quizzer(self.addb, self.path_addb)

    def mainloop(self):
        while True:

            s_ipt =  s_yellow(s_bold("### AdapDict ###"))
                    + "what do you want to do?\n"
                    + "  \"{}\": adaptive word quiz\n".format(s_green("quiz"))
                    + "  \"{}\": search or add a single WORD in the DB. put \'_\' instead of space for WORD like \'see_about\'.\n".format(s_green("find WORD"))
                    + "  \"{}\": add words in the csvs/NAME_CSV in the DB. you can skip including \'.csv\'.\n".format(s_green("add NAME_CSV"))
                    + "  \"{}\": quit. will save the changes made automatically\n".format(s_green("quit"))

            ipt = input(s_ipt)

            ipt_split = ipt.split(' ')
            if ipt_split[0] == 'quiz':
                s_ipt_quiz = "options in the form of \"NUM_WORD(5~100) SORT_CRITERION(\'impf\' or \'vn\') SELECTION(\'sort\' or \'sample\')\"\n"
                             + "(default: 10 impf sample) : "
                opt0 = input(s_ipt_quiz)
                try:
                    opt0_split = opt0.split(' ')
                    n_wds = int(opt0_split[0])
                    if n_wds > 4 and n_wds < 101: opt1 = [n_wds]
                    if opt0_split[1] in ['impf', 'vn']: opt1.append(opt0_split[1])
                    else: opt1.append('impf')
                    if opt0_split[2] in ['sort', 'sample']: opt1.append(opt0_split[1])
                    else: opt1.append('sample')
                except:
                    print("set to default option, \'10 impf sample\'")
                    opt1 = [10, 'impf', 'sample']
                self.quizzer.quiz_sample(opt1[0], opt1[1], opt1[2])

            elif ipt_split[0] == 'find':
                try:
                    print("will try to find {}".format(s_yellow(ipt_split[1])))
                    if self.addb.exist_word(ipt_split[1]):
                        self.addb.words[ipt_split[1]].print_part(show_mean = True, num_means = -1)
                        self.addb.words[ipt_split[1]].view_this(True)
                    else:
                        print("finding {} failed, below are the search results in the DB".format(s_yellow(ipt_split[1])))
                        res_search = self.addb.search_word(ipt_split[1])
                        for w in res_search:
                            print("  " + s_yellow(w.name))
                        print("")
                        if self.ParsingManager.parse_word(ipt_split[1]):
                            print("succeeded to add {} to DB".format(s_yellow(ipt_split[1])))
                        
                    input("enter anything to continue")

                except Exception as e:
                    print(e)
                    input("EXCEPTION, try again! (enter anything to continue)")

            elif ipt_split[0] == 'add':
                try:
                    self.ParsingManager.parse_csv(ipt_split[1])

                    input("enter anything to continue")

                except Exception as e:
                    print(e)
                    input("EXCEPTION, try again! (enter anything to continue)")

            elif ipt_split[0] == 'quit':
                self.quizzer.update_addb()
                print("bye!")
                break