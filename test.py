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
import ast
import datetime
import json
from collections import Counter
import time
import os.path
import matplotlib.pyplot as plt
import requests

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Button, Range
from bokeh.models.widgets import Slider, TextInput, DataTable, TableColumn, DatePicker
from bokeh.plotting import figure
from bokeh.events import ButtonClick


# Set up data
with open('corpus2.txt') as f:
    data = ast.literal_eval(f.read())

with open('top_ten.txt') as f:
    top_ten = ast.literal_eval(f.read())


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

x = [[]]
y = [[]]
group = ['legend']
color=['red']
columns = [
    TableColumn(field="ngram", title="NGram"),
    TableColumn(field="frequency", title="Frequency")
]
source = ColumnDataSource(data=dict(x=x, y=y, group=group, color=color))
table_source = ColumnDataSource(data=dict())

# Set up plot
plot = figure(x_axis_type="datetime", plot_height=700, plot_width=700, y_range=(0,100), title="look up words or phrases (up to three words) separated by a ','",
              tools="pan,reset,save,wheel_zoom")

plot.multi_line(xs='x', ys='y', legend='group', source=source, line_color='color', line_width=3, line_alpha=0.6)

data_table = DataTable(source=table_source, columns=columns, width=600)


# Set up widgets
phrase = TextInput(title="Graph this word or phrase:", value='')

datepicker1 = DatePicker(title="Start Date:", min_date=datetime.datetime(2018,1,1),
                       max_date=datetime.datetime.now(),
                       value=datetime.datetime(2018,4,1)
                       )

datepicker2 = DatePicker(title="End Date:", min_date=datetime.datetime(2018,1,1),
                       max_date=datetime.datetime.now(),
                       value=datetime.datetime.now()
                       )

datepicker3 = DatePicker(title="(This will take ~5 mins per day)\n Update Corpus to:", min_date=datetime.datetime(2018,1,1),
                       max_date=datetime.datetime.now(),
                       value=datetime.datetime.now()
                       )

button = Button(label="Update Corpus")

def update_data(attrname, old, new):
    
    d1 = datetime.datetime.combine(datepicker1.value, datetime.time())
    d2 = datetime.datetime.combine(datepicker2.value, datetime.time())
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
        date = datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S')
        if date >= d1 and date <= d2:
            tt = dict(Counter(tt)+Counter(top_ten[d]))
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

    source.data = dict(x=x_list, y=y_list, group=group_list, color=color_list)

phrase.on_change('value', update_data)
datepicker1.on_change('value', update_data)
datepicker2.on_change('value', update_data)

def chat_text(ticket):
    url_comments = zendesk + '/api/v2/tickets/' + str(ticket['id']) + '/comments.json'
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
    url_comments = zendesk + '/api/v2/tickets/' + str(ticket['id']) + '/comments.json'
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

def callback(event):
    credentials = 'kirk@baller.tv', 'Baller*269'
    session = requests.Session()
    session.auth = credentials
    zendesk = 'https://ballertv.zendesk.com'

    url = zendesk + '/api/v2/incremental/tickets.json?start_time=1514764800'
    tier1_codes = ['billing', 'product', '404error', 'partnerquestion', 'forgotpassword', 'eventpass']
    start_at = 1
    count = 0
    while url:
        tickets = []
        response = session.get(url)
        if response.status_code != 200:
            print('Error with status code {}'.format(response))
            break

        data = response.json()
        if count >= start_at:
            time.sleep(30)
            for ticket in data['tickets']:
                ticketdict = {}
                if len(list(set(ticket['tags']) & set(tier1_codes))) > 0:
                    if 'zopim_chat_ended' in ticket['tags']:
                        text = chat_text(ticket)
                    else:
                        text = not_chat_text(ticket)
                    if text:
                        ticketdict['id'] = ticket['id']
                        ticketdict['created_at'] = ticket['created_at']
                        ticketdict['tags'] = ticket['tags']
                        ticketdict['text'] = text
                        tickets.append(ticketdict)
            if len(tickets) > 0:
                with open('/Users/ballertvdev/Documents/tickets/tickets' + str(count) + '.txt', 'w') as json_file:
                    json.dump(tickets, json_file)
        print(count)
        count += 1
        url = data['next_page']

button.on_event(ButtonClick, callback)

# Set up layouts and add to document
inputs = column(phrase, datepicker1, datepicker2, datepicker3, button)

curdoc().add_root(row(inputs, plot, data_table, width=800))
curdoc().title = "NGram Viewer"