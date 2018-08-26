#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from chatterbot import ChatBot
from datetime import datetime
from chatterbot.trainers import ListTrainer
from chatterbot.conversation import Statement
from googlesearch import search
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)
import nltk
import math
import operator
import time
import os,sys
import random
import codecs


class NumericStringParser(object):
    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])
    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')
    def __init__(self):
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        self.bnf = expr
        epsilon = 1e-12
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {"sin": math.sin,
                   "cos": math.cos,
                   "tan": math.tan,
                   "exp": math.exp,
                   "abs": abs,
                   "trunc": lambda a: int(a),
                   "round": round,
                   "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0}
    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  
        elif op == "E":
            return math.e  
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)
    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val

files=[]
count=random.randint(0,10000)
if count not in files:
    filecount=count
else:
    filecount=count+1
ques=[]
ans=[]
filename='new_files/convo'+str(filecount)+'.txt'

bot=ChatBot("Pesank")

bot.set_trainer(ListTrainer)

sentiana=SentimentIntensityAnalyzer()

'''
for _file in os.listdir("files"):
    #chats=codecs.open("files/"+_file, "r",encoding='utf-8', errors='ignore').readlines() #this takes time
    chats=open("files/"+_file,"r").readlines()
    bot.train(chats)
'''

chat=True
while chat==True:
    request=raw_input("You: ")
    sa=sentiana.polarity_scores(request)
    print 'Sentiment Analysis=>',
    for word in sa:
        print('{0}: {1}, '.format(word, sa[word])),
    print ''
    ques.append(request)
    if(request=="terminate" or request=="bye" or request=="bye bye" or request=="okay bye bye" or request=="okay bye"):
        chat=False
    elif(request=="what is the date" or request=="what is today's date" or request=="what is todays date" or request=="what is the time now" or request=="what is the time"):
        response=time.asctime( time.localtime(time.time()))
        ans.append(response)
        print "Bot: ", response
    elif "math" in request:
        mathsum=[]
        count=0
        for integer in str(request):
            if 97<=ord(integer)<=122 or integer==" ":
                count+=1
            else:
                mathsum.append(integer)
        question=''.join(mathsum)
        nsp=NumericStringParser()
        response=nsp.eval(str(question))
        ans.append(response)
        print "Bot: ", response     
    else:
        response=bot.get_response(request)
        if(response.confidence>.35):
            ans.append(response)
            print "Bot:", response
            response=str(response)
            sa=sentiana.polarity_scores(response)

            for word in sa:
                print('{0}: {1}, '.format(word, sa[word])),
            print ''
        else:
            print "Bot: i am not sure, but you can refer these links\n"
            response=search(request, tld="co.in", num=10, stop=1, pause=2)
            ans.append(response)    
            searchresult=[]
            for i in response:
                    searchresult.append(i)
            for i in range(0,5):
                print "Bot:", searchresult[i]
            print "\nBot: i hope i helped you"
    
print "Bot: bye, it was nice chatting to you"
#print "Bot: please dont close the window\n"

file=open(filename, "w+")
for i in range(0,len(ans)):
    file.write(str(ques[i])+'\n')
    file.write(str(ans[i])+'\n')
file.close()

#print "Bot: now let me train myself from what we have discussed\n"
#print "Bot: wait for sometime, this will help me in future\n"

'''
for _file in os.listdir("files"):
    chats=codecs.open("files/"+_file, "r",encoding='utf-8', errors='ignore').readlines() #this takes time
    #chats=open("new_files/"+_file,"r").readlines()
    bot.train(chats)
'''

print "Bot: and dont forget to delete google cookie or just eat it if its present\n"
#print "Bot: thank you for waiting, bye now, hope to see you again :)\n"
