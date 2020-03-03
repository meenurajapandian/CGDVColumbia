#%%
import pandas as pd
import numpy as np
import json
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import TapTool, GeoJSONDataSource, NumeralTickFormatter, LinearColorMapper, LogColorMapper
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import column, row

from bokeh.palettes import brewer
from bokeh.io import show #To be removed later


# PLOT 1 : Bar plot for countries taking in Venezuelans
# Can try side by side instead of stack

df = pd.read_csv("c_people_from_ven.csv")
df['Total'] = df.sum(axis=1)

years = list(range(2000, 2019))
years = [str(year) for year in years]


y = np.zeros(len(years)).tolist()
s12 = ColumnDataSource(data=dict(x=years, y=y))

p12 = figure(plot_width=500, plot_height=280, title="Select a country to see more", toolbar_location=None)
p12.line(x='x', y='y', source=s12, line_width=2)

p12.outline_line_alpha = 0

p12.xaxis.axis_line_color = "#575757"
p12.xaxis.minor_tick_line_color = None
p12.xaxis.major_tick_line_color = "#878787"
p12.xaxis.major_tick_out = 1


p12.y_range.start = 0
p12.yaxis.axis_line_color = "#575757"
p12.yaxis.minor_tick_line_color = None
p12.yaxis.major_tick_line_color = "#878787"
p12.xaxis.major_tick_out = 1
p12.yaxis.formatter = NumeralTickFormatter(format="0.0a")


filtered = df.nlargest(5,'Total')
Country = filtered['Country'].tolist()
Country.reverse()
s11 = ColumnDataSource(filtered)

p11 = figure(y_range=Country, plot_width=500, plot_height=280, title="Refugee Intake", toolbar_location="above", tools="hover", tooltips="Refugees: @2018")
p11.hbar(right='2018', y='Country', height=0.70, source=s11)

p11.outline_line_alpha = 0

p11.yaxis.axis_line_color = "#575757"
p11.yaxis.major_tick_line_color = None
p11.yaxis.major_tick_out = 1
p11.ygrid.grid_line_color = None

p11.x_range.start = 0
p11.xaxis.axis_line_color = None
p11.xaxis.minor_tick_line_color = None
p11.xaxis.major_tick_line_color = "#878787"
p11.xaxis.major_tick_out = 1
p11.xaxis.formatter = NumeralTickFormatter(format="0.0a")

#p11.hover.tooltips=["Click to find out more"]

callback1 = CustomJS(args=dict(s11=s11,s12=s12), code=
"""
var inds = cb_data.source.selected['1d'].indices
var d1 = s11.data
var d2 = s12.data
d2['y'] = []

//var year = 2018
//console.log(d1['2018'][0])
//console.log(d1[year.toString(10)][0])


for (var i = 2000; i<2019; i++) {
    d2['y'].push(d1[i.toString(10)][inds])
}

s12.change.emit()
""")
p11.add_tools(TapTool(callback=callback1))


# Stacked Bar plot for a few years
# colors = brewer['Set3'][len(years)]
# colors.reverse()
# p1 = figure(y_range=Country, plot_height=500, title="Refugee Intake",
#            toolbar_location=None, tools="hover", tooltips="$name @Country: @$name")
# p1.hbar_stack(years, y='Country', height=0.4, color=colors, source=ColumnDataSource(filtered), legend_label=years)
#
# p1.x_range.start = 0
# p1.x_range.end = max(df['Total'])
# p1.y_range.range_padding = 0.1
# p1.ygrid.grid_line_color = None
# p1.axis.minor_tick_line_color = None
# p1.outline_line_color = None
# p1.legend.location = "bottom_right"
# p1.legend.orientation = "vertical"


# show(row(p11, p12))


# PLOT 2 : Colombia demographics

df = pd.read_csv("c_demo_colombia.csv",dtype=str)

dataToAdd = df.set_index('DPTO').T.to_dict('list')

with open('Colombia.geojson', 'r') as f:
    data = json.load(f)


for feat in data['features']:
    ToAdd = dataToAdd[feat['properties']['DPTO']]
    feat['properties']['Refugees'] = ToAdd[1]
    feat['properties']['Area'] = ToAdd[2]
    feat['properties']['Population'] = ToAdd[3]
    feat['properties']['Unemployment'] = ToAdd[4]
    feat['properties']['Poverty'] = ToAdd[5]
    feat['properties']['Illiteracy'] = ToAdd[6]


with open('new.geojson', 'w') as f:
    json.dump(data, f)


with open(r'new.geojson') as f:
    geo_src = GeoJSONDataSource(geojson=f.read())

palette = brewer['OrRd'][9]
palette.reverse()
color_mapper = LogColorMapper(palette=brewer['OrRd'][9])

p21 = figure(x_axis_location=None, y_axis_location=None, width=580, height=680)
p21.grid.grid_line_color = None

p21.patches('xs', 'ys', fill_color={'field': 'Refugees', 'transform': color_mapper}, fill_alpha=0.8, line_color='black',
            line_width=0.5, line_alpha=0.8, source=geo_src, legend_field='Refugees')

callback2 = CustomJS(args=dict(s1=geo_src), code=
    """
    var inds = cb_data.source.selected['1d'].indices
    console.log(cb_data.source.selected)
    var d1 = s1.data
    console.log(d1['NOMBRE_DPT'][inds])
    """)
p21.add_tools(TapTool(callback=callback2))


p21.x_range.start = -80
p21.x_range.end = -66

p21.y_range.start = -5
p21.y_range.end = 13


show(p21)

# Once done list all plots in a dictionary and generate script and div boxes to be added in the html file.
# plots = {'plot1': p11, 'plot2': p12}
#
# script, div = components(row(p11, p12))
# print(script)
# print(div)

