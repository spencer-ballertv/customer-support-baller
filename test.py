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
import ast
import datetime
import json

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure
from bokeh.models.widgets import DatePicker
from bokeh.events import ButtonClick
from bokeh.models import Button

# Set up data
with open('corpus2.txt') as f:
    data = ast.literal_eval(f.read())

print(len(data))

weeks = []
date = datetime.datetime.now().date()
wd = date.weekday()
if wd != 6:
    date = date - datetime.timedelta(wd + 1)
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
source = ColumnDataSource(data=dict(x=x, y=y, group=group, color=color))
table_source = ColumnDataSource(data=dict())

# Set up plot
plot = figure(x_axis_type="datetime", plot_height=700, plot_width=700, title="look up words or phrases (up to three words) separated by a ','",
              tools="pan,reset,save,wheel_zoom")

plot.multi_line(xs='x', ys='y', legend='group', source=source, line_color='color', line_width=3, line_alpha=0.6)


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


    for e in range(len(p)):
        p[e] = p[e].strip()
        for w in weeks:
            if w not in data[p[e]]:
                data[p[e]][w] = 0

        t = list(data[p[e]].keys())
        t.sort()
        x = []
        for n in range(len(t)):
            date = datetime.datetime.strptime(t[n],'%Y-%m-%d %H:%M:%S')
            if date >= d1 and date <= d2:
                x.append(date)
        y = [data[p[e]][m] for m in t]
        x_list.append(x)
        y_list.append(y)
        group_list.append(p[e])
        col = e % 8
        color_list.append(colors[col])

    source.data = dict(x=x_list, y=y_list, group=group_list, color=color_list)

phrase.on_change('value', update_data)
datepicker1.on_change('value', update_data)
datepicker2.on_change('value', update_data)


def callback(event):
    print('Python:Click')

button.on_event(ButtonClick, callback)

# Set up layouts and add to document
inputs = column(phrase, datepicker1, datepicker2, datepicker3, button)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "NGram Viewer"