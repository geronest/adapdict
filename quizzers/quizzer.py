# -*- coding: utf-8 -*-
import random
import numpy as np
import pickle as pkl
from fddb import FreqDictDB
from infos import MeanInfo, WordInfo

class Quizzer():
    def __init__(self, fddb):
        self.fddb = fddb

    def quiz_sample(self, num_words = 10, criterion = 'impf', method = 'sort'):
        ws = self.fddb.select_words(num_words = num_words, criterion = criterion, method = method)
        for w in ws:
            pass # TODO: check if the user knows this word, process accordingly


