from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import Prompt, Resource

from .utils.model import *
from .utils.helpers import *

import os
current_path = os.path.abspath(os.path.dirname(__file__))

import language_check
import csv, io

#Firebase 
import pyrebase

#Grammer Scoring
import model
import dill
import sys

#Spelling Scoring
from spellchecker import SpellChecker
import re

config = {
    'apiKey': "AIzaSyAFoPMs-pbtJH87BFqJC4CElayXjDzjFpw",
    'authDomain': "splash-brown.firebaseapp.com",
    'databaseURL': "https://splash-brown.firebaseio.com",
    'projectId': "splash-brown",
    'storageBucket': "splash-brown.appspot.com",
    'messagingSenderId': "845602928402",
    'appId': "1:845602928402:web:367acba0aebb82fb4f65cb",
    'measurementId': "G-5S7VJBC2R5"
}

firebase = pyrebase.initialize_app(config) 
auth = firebase.auth()
db = firebase.database()

# Create your views here.
def index(request):
    return render(request, 'dev/login.html')

def login(request):
    if request.method=='POST':
        try:
            formId = request.POST['formId']
            if formId=='login':
                email=request.POST['email']
                password=request.POST['password']
                user = auth.sign_in_with_email_and_password(email, password)
                message='Successful sign-in!'
                session_id=user['idToken']
                request.session['uid']=str(session_id)
                #print(user)
                return redirect('userhome')
                
            else:
                email=request.POST['reg-email']
                password=request.POST['reg-password']
                user = auth.create_user_with_email_and_password(email, password)
                message='Successful registration!'
                udata = {'email':email, 'learner-type':'default', 'p-interest':'default', 's-interest':'default', 'level':'Beginner', 'score':0}
                db.child('users').child('testing').set(udata)
                #print(user)
                return redirect('profile')
           
        except:
            message="Invalid credentials"
            return render(request,'dev/login.html', {"msg":message})
           
    else:
        return render(request, 'dev/login.html')

def logout(request):
    try:
        del request.session['uid']
        #print("Logged out!" )
    except KeyError:
        pass
    return redirect('index')

def profile(request):
    if request.method=='POST':
        udata = {'learner-type':request.POST['learner-type'], 
            'p-interest':request.POST['p-interest'], 
            's-interest':request.POST['s-interest']
            }
        db.child('users').child('testing').update(udata)
        return redirect('index')
    else:
        return render(request, 'dev/profile.html')

def userhome(request):
    return render(request, 'dev/dashboard.html')

def topics(request):
    return render(request, 'dev/topics.html')

def essay(request):
    return render(request, 'dev/essay.html')

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():

            content = form.cleaned_data.get('answer')


            K.clear_session()
            essay = Essay.objects.create(
                content=content,
                question=question,
                score=preds
            )

        return redirect('essay', question_id=question.set, essay_id=essay.id)
    
    else:
        form = AnswerForm()

        context = {
            "question": question,
            "form": form,
        }
        return render(request, 'grader/question.html', context)




def scoring(request):
    if request.method=='POST':
        submitted=request.POST['essaycontent']
        tool = language_check.LanguageTool('en-GB')
        matches = tool.check(submitted)
        wordcount = str(len(submitted.split()))
        #print(wordcount)
        #print(submitted)
        #print(type(submitted))
        display=""
        count = 1
        for i in matches:
            display+=str(count) + '. ' + str(i.msg) + "\n"+ ' Replacement: ' + str(i.replacements[0])
            display += '\n'
            count += 1
        display = display.replace('<br>', '\n')
        display = display.replace('^', '')
        #print(display)
        if len(display)==0:
            display="No errors found."

        import pandas as pd
        from nltk.tokenize import word_tokenize
        import gensim
        LDA = gensim.models.ldamodel.LdaModel 
        ldamodel = LDA.load("grader/deep_learning_files/ldatest")
        dictionary = ldamodel.id2word
        
        MAXTOPICS = 20
        topics = ldamodel.show_topics(formatted=True, num_topics=MAXTOPICS, num_words=3)

        testdoc = submitted
        cleandoc = word_tokenize(testdoc)
        resdf=pd.DataFrame([(el[0], round(el[1],2), topics[el[0]][1]) for el in ldamodel[dictionary.doc2bow(cleandoc)]], columns=['topic #', 'weight', 'words in topic']).sort_values(by=['weight'], ascending=False)
    
        testqn = "How far should religion influence political decisions ?"
        cleandoc = word_tokenize(testqn)
        qndf=pd.DataFrame([(el[0], round(el[1],2), topics[el[0]][1]) for el in ldamodel[dictionary.doc2bow(cleandoc)]], columns=['topic #', 'weight', 'words in topic']).sort_values(by=['weight'], ascending=False)
        
        found=0
        if resdf['weight'].max()-resdf['weight'].min()==0:
            found=0
        else:
            for topic in list(qndf['topic #'])[:3]:
                if topic in resdf['topic #'].unique():
                    found+=round(resdf.set_index('topic #').loc[topic]['weight'], 2)
                    break
        
        udata=db.child('users').child('testing').get()

        while True:
            # Load model
            with open(r"training/model.dill", 'rb') as file:
                model = dill.load(file)
            if submitted != '' and model.rate(submitted) > 0:
                grammarscore = str(model.rate(submitted)) + "0%"
                print("Score: {}/10".format(model.rate(submitted)))
            else:
                grammarscore = "0%"

            break

        spell = SpellChecker() 

        def spelling_score(submitted, wordcount): 

            #remove punctuation and split text into a list of words
            res = re.sub(r'[^\w\s]', '', submitted)
            txt = res.split()

            # find those words that may be misspelled 
            # misspelled = spell.unknown(["cmputr", "water", "study", "wrte"]) 
            misspelled = spell.unknown(txt)
            #only misspelled words appear in misspelled 
            
            # can omit this since overlaps with correction function
            for word in misspelled: 

                # Get the one `most likely` answer 
                print(spell.correction(word)) 
            
                # Get a list of `likely` options 
                # print(spell.candidates(word)) 

            errors = len(misspelled)
            score = (int(wordcount) - errors)/int(wordcount) * 100
            return score

        spellingscore = str(round(spelling_score(submitted, int(wordcount))))
        if spelling_score(submitted, int(wordcount)) != 0:
            spellingscore += "%"
            print(spellingscore + "%")
        else:
            spellingscore="0%"
            print(spellingscore)
                    
        rel = str(int(round(found*100))) + "%"
        print(rel + "RELEVANCE")
        rsc_list=Resource.objects.filter(content_type='Grammar')
        context = {
            'display':display, 
            'relevance': rel,
            "rsc_list" : rsc_list,
            "wordcount": wordcount,
            "submitted": submitted,
            "grammarscore": grammarscore,
            "spellingscore": spellingscore
        }
        #print(context)
        return render(request, 'dev/scoring.html', context)
    

   

#Upload CSV files to Django database [ADMIN ONLY]
@permission_required('admin.can_add_log_entry')
def accessdb(request):
    context = {
        'instructions': 'CSV file must contain specified columns in order.'
    }

    if request.method =='GET':
        return render(request, 'grader/accessdb.html', context)
    
    csv_file = request.FILES["file"]

    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV file accepted.")
    
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    if (request.POST['db']=='Prompts'):
        for column in csv.reader(io_string, delimiter=',', quotechar='|'):
            _, created = Prompt.objects.update_or_create(
            id=column[0],
            area=column[1],
            prompt=column[2]
            )
    elif (request.POST['db']=='Resources'):
        for column in csv.reader(io_string, delimiter=',', quotechar='|'):
            _, created = Resource.objects.update_or_create(
            learner_type=column[0],
            content_type=column[1],
            link=column[2],
            beginner=column[3],
            intermediate=column[4],
            advanced=column[5]
            )
    else:
        messages.error(request, "Only databases shown exist.")
    context={}
    return render(request, 'grader/accessdb.html', context)