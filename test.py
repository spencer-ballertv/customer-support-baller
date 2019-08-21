''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
import numpy as np
import pandas as pd
import zenpy as zp
import ast
import datetime
import json
from collections import Counter
import time
import os.path
import requests
from sklearn.feature_extraction.text import CountVectorizer 
import re
import github
from textblob import TextBlob

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Button, Range, LabelSet, HoverTool
from bokeh.models.widgets import Slider, TextInput, DataTable, TableColumn, DatePicker, CheckboxGroup
from bokeh.plotting import figure
from bokeh.events import ButtonClick

stop_words = [
   "241", "260", "2bphh", "360000264512", "427", "4646", "626", "6928", "a", "about", "above", "across", "after", "afterwards", "again", "against",
   "almost", "alone", "along", "already", "also", "although", "always",
   "am", "amanda", "among", "amongst", "amoungst", "an", "and",
   "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "aol", "are",
   "around", "as", "at", "back", "baller", "ballet", "ballertv", "balr", "be", "became", "because", "become",
   "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
   "below", "beside", "besides", "between", "beyond", "bill", "both",
   "bottom", "but", "by", "call", "can", "carroll", "co", "con",
   "could", "cry", "de", "describe", "detail", "did", "do", "done", "dorantes"
   "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
   "elsewhere", "empty", "enough", "eric", "etc", "even", "ever", "every", "everyone",
   "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
   "find", "fire", "first", "five", "for", "former", "formerly", "forty",
   "found", "four", "from", "front", "full", "further", "get", "gino", "give", "gmail", "go", "greg",
   "had", "has", "have", "he", "hence", "hensley", "hello", "her", "here", "hereafter",
   "hereby", "herein", "hereupon", "hers", "herself", "hey", "hi", "him", "himself", "his",
   "how", "however", "httpswwwballertvstreamsnextleveleclipsegrayvsswarmblackrichie", "hundred", "husband", "i", "ie", "if", "im", "in", "inc", "indeed",
   "interest", "into", "is", "it", "its", "itself", "janelle", "jennifer", "john", "joyce", "just", "kaj", "keep", "last", "latter",
   "latterly", "lawrence", "least", "less", "ll", "ltd", "made", "many", "marc", "maria", "sanogal", "may", "me",
   "meanwhile", "melgarejo", "merged", "might", "mill", "miller", "mine", "mj", "more", "moreover", "most", "mostly",
   "move", "much", "must", "my", "myself", "name", "namely", "neither",
   "never", "nevertheless", "next", "nine", "nobody", "none", "noone",
   "nor", "nowhere", "of", "off", "often", "ok", "on",
   "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
   "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
   "please", "put", "r3xecg9oeir8g6isrkdq5o5ojyqaetkrrn", "rather", "re", "regards", "same", "see", "seem", "seemed",
   "seeming", "seems", "serious", "several", "she", "should", "show", "side",
   "since", "sincere", "sincerely", "six", "sixty", "so", "some", "somehow", "someone",
   "something", "sometime", "sometimes", "somewhere", "spiece", "steph", "still", "such", "supportballertv",
   "system", "t", "take", "ten", "than", "thank", "thanks", "that", "thatcher", "thats", "the", "their", "them",
   "themselves", "then", "thence", "there", "thereafter", "thereby",
   "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
   "third", "this", "those", "though", "three", "through", "throughout",
   "thru", "thus", "thx", "to", "together", "too", "top", "toward", "towards", "tv",
   "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
   "very", "via", "ve", "was", "we", "well", "were", "what", "whatever", "when",
   "whence", "whenever", "where", "whereafter", "whereas", "whereby",
   "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
   "who", "whoever", "whole", "whom", "whose", "why", "wife", "will", "with",
   "within", "without", "would", "wwwxsportfitnesscom", "xsport_fitness_", "yahoo", "yes", "yet", "you", "your", "yours", "yourself",
   "yourselves"]


# Set up data
with open('corpus.txt') as f:
    data = ast.literal_eval(f.read())

with open('cumul.txt') as f:
    top_ten = ast.literal_eval(f.read())

with open('norm2.txt') as f:
    norm = ast.literal_eval(f.read())

with open('time.txt') as f:
    time = ast.literal_eval(f.read())

files = [data, top_ten, norm]

for file in files:
    if type(file) == str:
        file = dict(file)


time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')

title = "Last Corpus Update: " + str(time)


weeks = []
date = datetime.datetime.now().date()
wd = date.weekday()
if wd != 0:
    date = date - datetime.timedelta(wd)
    date = datetime.datetime.combine(date, datetime.time())
    str_date = str(date)
weeks.append(str_date)
week = date
while week > datetime.datetime(2018,4,1):
    week = week - datetime.timedelta(7)
    weeks.append(str(week))

for w in weeks:
    if w not in norm:
        norm[w] = 1

x = [[]]
y = [[]]
group = ['legend']
color=['red']
columns = [
    TableColumn(field="ngram", title="NGram"),
    TableColumn(field="frequency", title="Frequency")
]
source = ColumnDataSource(data=dict(date=x, freq=y, group=group, color=color))
table_source = ColumnDataSource(data=dict())

# Set up plot
plot = figure(x_axis_type="datetime", plot_height=700, plot_width=700, y_range=(0,100), title=title,
              tools="pan,save,wheel_zoom")

plot.multi_line(xs='date', ys='freq', legend='group', source=source, line_color='color', line_width=3, line_alpha=0.6, hover_line_color='color', hover_line_alpha=1.0)

hover = HoverTool(tooltips=[('Date','$x{%F}'), 
                        ('Frequency','$y{0}')], 
              formatters={'$x': 'datetime'},
              mode = 'mouse',
             line_policy='nearest')

plot.add_tools(hover)

data_table = DataTable(source=table_source, columns=columns, width=600)


# Set up widgets
phrase = TextInput(title="Graph these comma-separated phrases:", value='')

datepicker1 = DatePicker(title="Start Date:", min_date=datetime.datetime(2018,4,1),
                       max_date=datetime.datetime.now(),
                       value=datetime.datetime(2018,4,15)
                       )

datepicker2 = DatePicker(title="End Date:", min_date=datetime.datetime(2018,4,16),
                       max_date=datetime.datetime.now(),
                       value=datetime.datetime.now()
                       )


checkbox_group = CheckboxGroup(
        labels=["Normalize"])

button = Button(label="Update Corpus")

def update_data(attrname, old, new):    
    d1 = datetime.datetime.combine(datepicker1.value, datetime.time())
    d2 = datetime.datetime.combine(datepicker2.value, datetime.time())
    wd1 = d1.weekday()
    wd2 = d2.weekday()
    d1 = d1 - datetime.timedelta(wd1)
    d2 = d2 - datetime.timedelta(wd2)
    p = phrase.value
    p = p.split(",")
    x_list = []
    y_list = []
    group_list = []
    color_list = []
    colors = ['red', 'blue', 'green', 'purple', 'black', 'pink', 'orange', 'brown']
    indices = [0,0]
    done = 0
    tt = {}

    for d in top_ten:
        if str(d1) not in top_ten and str(d2) not in top_ten:
            date = str(d2)
            while date not in top_ten:
                date = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
                date = date - datetime.timedelta(7)
                date = str(date)

            count_freq = Counter(top_ten[date])
            top_10 = count_freq.most_common(10)
        elif str(d1) not in top_ten:
            count_freq = Counter(top_ten[str(d2)])
            top_10 = count_freq.most_common(10)
        elif str(d2) not in top_ten:
            date = str(d2)
            while date not in top_ten:
                date = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
                date = date - datetime.timedelta(7)
                date = str(date)

            tt = dict(Counter(top_ten[date])-Counter(top_ten[str(d1)]))
            count_freq = Counter(tt)
            top_10 = count_freq.most_common(10)
        else:
            tt = dict(Counter(top_ten[str(d2)])-Counter(top_ten[str(d1)]))
            count_freq = Counter(tt)
            top_10 = count_freq.most_common(10)

        
    df = pd.DataFrame(top_10, columns=["ngram", "frequency"])
    table_source.data = {
        'ngram' : df.ngram,
        'frequency' : df.frequency
    }

    for e in range(len(p)):
        p[e] = p[e].strip()
        for w in weeks:
            if w not in data[p[e]]:
                data[p[e]][w] = 0

        t = list(data[p[e]].keys())
        t.sort()
        new = []
        x = []
        for n in range(len(t)):
            date = datetime.datetime.strptime(t[n],'%Y-%m-%d %H:%M:%S')
            if date >= d1 and date <= d2:
                new.append(t[n])
                x.append(date)
        y = [data[p[e]][m] for m in new]
        x_list.append(x)
        y_list.append(y)
        group_list.append(p[e])
        col = e % 8
        color_list.append(colors[col])
    y_max = 1
    for lst in y_list:
        if max(lst) > y_max:
            y_max = max(lst)
    y_max += (y_max * 0.1)

    plot.y_range.end = y_max

    source.data = dict(date=x_list, freq=y_list, group=group_list, color=color_list)
    

phrase.on_change('value', update_data)
datepicker1.on_change('value', update_data)
datepicker2.on_change('value', update_data)
checkbox_group.on_change('active', update_data)


def normalize(atrr, old, new):
    d1 = datetime.datetime.combine(datepicker1.value, datetime.time())
    d2 = datetime.datetime.combine(datepicker2.value, datetime.time())
    wd1 = d1.weekday()
    wd2 = d2.weekday()
    d1 = d1 - datetime.timedelta(wd1)
    d2 = d2 - datetime.timedelta(wd2)

    t = list(norm.keys())
    t.sort()
    new = []
    for n in range(len(t)):
        date = datetime.datetime.strptime(t[n],'%Y-%m-%d %H:%M:%S')
        if date >= d1 and date <= d2:
            new.append(t[n])
    num_ticks = [norm[m] for m in new]

    new_y = []

    if checkbox_group.active == [0]:
        
        for y in source.data['freq']:
            divide = [a/b for a, b in zip(y, num_ticks)]
            new_y.append(divide)
    else:
        for y in source.data['freq']:
            new_y.append(y)

    y_max = 0.1
    for lst in new_y:
        if max(lst) > y_max:
            y_max = max(lst)
    y_max += (y_max * 0.1)

    plot.y_range.end = y_max
    source.data['freq'] = new_y


    
checkbox_group.on_change('active', normalize)
phrase.on_change('value', normalize)
datepicker1.on_change('value', normalize)
datepicker2.on_change('value', normalize)

def chat_text(ticket):
    zendesk = 'https://ballertv.zendesk.com'
    credentials = 'btv.billrussell@gmail.com', '5time-MVP'
    session = requests.Session()
    session.auth = credentials
    url_comments = zendesk + '/api/v2/tickets/' + str(ticket.id) + '/comments.json'
    response_comments = session.get(url_comments)
    if response_comments.status_code != 200:
        print('Error with status code for comment {}'.format(response_comments.status_code))
        return ''
    comment_data = response_comments.json()
    if len(comment_data['comments']) > 2:
        tickettext = ''
        nametext = comment_data['comments'][2]['body'].split('\n')
        if len(nametext) < 3:
            return ''
        name = nametext[2]
        if 'Name: ' not in name:
            return ''
        name = name[6:]
        chat = comment_data['comments'][1]['body'].split('\n')
        for line in chat:
            if (name + ': ') in line:
                ind = line.index(name + ': ')
                tickettext = tickettext + ' ' + line[(ind + len(name) + 2):]
        for c in range(len(comment_data['comments']) - 3):
            tickettext = tickettext + ' ' + ' '.join(comment_data['comments'][c + 3]['body'].split('\n'))
        return tickettext
    else:
        return ''

def not_chat_text(ticket):
    zendesk = 'https://ballertv.zendesk.com'
    credentials = 'btv.billrussell@gmail.com', '5time-MVP'
    session = requests.Session()
    session.auth = credentials
    url_comments = zendesk + '/api/v2/tickets/' + str(ticket.id) + '/comments.json'
    response_comments = session.get(url_comments)
    if response_comments.status_code != 200:
        print('Error with status code for comment {}'.format(response_comments.status_code))
        return ''
    comment_data = response_comments.json()
    if len(comment_data['comments']) > 0:
        tickettext = ''
        for comment in comment_data['comments']:
            text = comment['body'].split('\n')
            if 'Chat started: 20' in text[0]:
                return ''
            if 'BallerTV Fan Support' in text or 'BallerTV Support' in text:
                continue
            else:
                text = ' '.join(text)
            tickettext = tickettext + ' ' +  text
        return tickettext
    else:
        return ''


def update_files(file, new_contents):
    user = "spencer-ballertv"
    password = "Harden#13"
    g = github.Github(user,password)
    repo = g.get_user().get_repo('customer-support-baller')

    master = requests.get('https://api.github.com/repos/spencer-ballertv/customer-support-baller/git/trees/master').json()

    for d in master["tree"]:
        if d["path"] == file:
            sha = d["sha"]

    commit_msg = "corpus pull: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    content = json.dumps(new_contents)

    repo.update_file(file, commit_msg, content, sha)

def callback(event):
    print("yo")
    creds = {
        'email' : 'btv.billrussell@gmail.com',
        'password' : '5time-MVP',
        'subdomain': 'ballertv'
    }
    zendesk = 'https://ballertv.zendesk.com'

    zenpy_client = zp.Zenpy(proactive_ratelimit=2500, **creds)

    tier1_codes = ['billing', 'product', '404error', 'partnerquestion', 'forgotpassword', 'eventpass']

    pull_time = datetime.datetime.now()# - datetime.timedelta(hours=7)

    pull_time = str(pull_time.strftime("%Y-%m-%d %H:%M:%S"))

    print("what up")
    yesterday = datetime.datetime.strptime(plot.title.text[20:],'%Y-%m-%d %H:%M:%S')
    today = datetime.datetime.now()
    count = 1
    tickets = []
    for ticket in zenpy_client.search(created_between=[yesterday, today], type='ticket'):
        ticketdict = {}
        if len(list(set(ticket.tags) & set(tier1_codes))) > 0:
            if 'zopim_chat_ended' in ticket.tags:
                text = chat_text(ticket)
            else:
                text = not_chat_text(ticket)
            if text:
                ticketdict['id'] = ticket.id
                ticketdict['created_at'] = ticket.created_at
                ticketdict['tags'] = ticket.tags
                ticketdict['text'] = text
                tickets.append(ticketdict)
        count += 1

    top_t_temp = {}

    for tick in tickets:
        print(count)

        text = tick["text"]
        text = re.sub(r'[^\w\s]','', text)
        text = re.sub(r'\w*\d\w*', '', text).strip()
        text = text.lower()
        text = TextBlob(text)
        text = str(text.correct())
        d = tick["created_at"]
        date = d.split('T')
        date = date[0]
        date = datetime.datetime.strptime(tick["created_at"].split("T")[0], '%Y-%m-%d')
        wd = date.weekday()
        if wd != 0:
            date = date - datetime.timedelta(wd)
        date = str(date)
        if date not in top_t_temp:
            top_t_temp[date] = {}
        if date in norm:
            norm[date] += 1
        if date not in norm:
            norm[date] = 1
        
        vectorizer = CountVectorizer(ngram_range=(1,3), stop_words = stop_words)
        analyzer = vectorizer.build_analyzer()
        grams = analyzer(text)
        
        for gram in grams:
            if gram not in top_t_temp[date] and gram != "no" and gram != "not":
                top_t_temp[date][gram] = 1
            
            if gram in top_t_temp[date]:
                top_t_temp[date][gram] += 1
                
            if gram not in data:
                data[gram] = {}
                data[gram][date] = 1
                
            if date not in data[gram]:
                data[gram][date] = 1
                
            else:
                data[gram][date] += 1
    top_t_keys = list(top_t_temp.keys())
    delete = []
    for key in top_t_keys:
        tt_lst = list(top_t_temp[key].keys())
        for k in tt_lst:
            if len(k.split()) > 1:
                del top_t_temp[key][k]
    top_t_keys = list(top_t_temp.keys())
    top_t_keys.sort()
    top_ten_keys = list(top_ten.keys())
    top_ten_keys.sort()
    top_ten_last_key = top_ten_keys[-1]
    top_ten[top_t_keys[0]] = dict(Counter(top_t_temp[top_t_keys[0]])+Counter(top_ten[top_ten_last_key]))
    for i in range(1, len(top_t_keys)):
        top_ten[top_t_keys[i]] = dict(Counter(top_t_temp[top_t_keys[i]])+Counter(top_ten[top_t_keys[i-1]]))
    print("hello")
    plot.title.text = "Last Corpus Update: " + pull_time
    update_files("corpus2.txt", data)
    print("check")
    update_files("cumulative.txt", top_ten)
    print("check")
    update_files("norm.txt", norm)
    print("check")
    update_files("time.txt", pull_time)

button.on_event(ButtonClick, callback)

# Set up layouts and add to document
inputs = column(phrase, datepicker1, datepicker2, checkbox_group, button)

curdoc().add_root(row(inputs, plot, data_table, width=800))
curdoc().title = "NGram Viewer"