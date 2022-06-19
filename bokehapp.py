import pandas as pd
import yfinance as yf

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, DataTable, TableColumn, Tabs, Panel
from bokeh.layouts import column, row
from bokeh.plotting import figure, show

DEFAULT_TICKERS = ["AAPL", "GOOG", "MSFT", "NFLX", "TSLA"]
START, END = "2018-01-01", "2022-01-01"


def load_ticker(tickers):
    df = yf.download(tickers, start=START, end=END)
    return df["Close"].dropna()


# static_data = load_ticker(DEFAULT_TICKERS)


def get_data(t1, t2):
    d = load_ticker(DEFAULT_TICKERS)
    df = d[[t1, t2]]
    returns = df.pct_change().add_suffix("_returns")
    df = pd.concat([df, returns], axis=1)
    df.rename(columns={t1: "t1", t2: "t2", t1 +
              "_returns": "t1_returns", t2+"_returns": "t2_returns"}, inplace=True)
    return df.dropna()


def nix(val, lst):
    return [x for x in lst if x != val]


ticker1 = Select(value="AAPL", options=nix("GOOG", DEFAULT_TICKERS))
ticker2 = Select(value="GOOG", options=nix("AAPL", DEFAULT_TICKERS))

# source data


data = get_data(ticker1.value, ticker2.value)
source = ColumnDataSource(data=data)

stats = round(data.describe().reset_index(), 2)
stats_source = ColumnDataSource(data=stats)
stat_columns = [TableColumn(field=col, title=col) for col in stats.columns]
data_table = DataTable(source=stats_source, columns=stat_columns,
                       width=350, height=350, index_position=None)

# Plots
corr_tools = "pan, wheel_zoom, box_select, reset"
tools = "pan, wheel_zoom, xbox_select, reset"

corr = figure(width=350, height=350, tools=corr_tools)
corr.circle("t1_returns", "t2_returns", size=2, source=source,
            selection_color="firbrick", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

ts1 = figure(width=700, height=250, tools=tools,
             x_axis_type="datetime", active_drag="xbox_select")

ts1.line("Date", "t1", source=source)
ts1.circle("Date", "t1", size=1, source=source,
           color=None, selection_color="firebrick")

ts2 = figure(width=700, height=250, tools=tools,
             x_axis_type="datetime", active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line("Date", "t2", source=source)
ts2.circle("Date", "t2", size=1, source=source,
           color=None, selection_color="firebrick")

# callback


def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()


def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()


def update(selected=None):
    t1, t2 = ticker1.value, ticker2.value
    df = get_data(t1, t2)
    source.data = df
    stats_source.data = round(df.describe().reset_index(), 2)
    corr.title.text = "%s returns vs. %s returns" % (t1, t2)
    ts1.title.text, ts2.title.text = t1, t2

    
    
def set_style(p):
    # Tick labels
    p.xaxis.major_label_text_font_size = '6pt'
    p.yaxis.major_label_text_font_size = '10pt'

ts1 = figure(width=700, height=250, tools=tools,
             x_axis_type="datetime", active_drag="xbox_select")

ts1.line("Date", "t1", source=source)
ts1.circle("Date", "t1", size=1, source=source,
           color=None, selection_color="firebrick")
tab1 = Panel(child=ts1, title = "tab1")

ts2 = figure(width=700, height=250, tools=tools,
             x_axis_type="datetime", active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line("Date", "t2", source=source)
ts2.circle("Date", "t2", size=1, source=source,
           color=None, selection_color="firebrick")
tab2 = Panel(child=ts2, title="tab2")

tabs = Tabs(tabs=[tab1, tab2])

set_style(ts1)
set_style(ts2)    
    

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)


widgets = column(ticker1, ticker2, data_table)
main_row = row(corr, widgets, tabs)
series = column(ts1, ts2)
layout = column(main_row, series)

update()

curdoc().add_root(layout)
curdoc().title = "Stock Dashboard"
