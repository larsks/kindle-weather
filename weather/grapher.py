import math

import matplotlib
matplotlib.use('cairo')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

def plot_common(data):
    dates = [mdates.epoch2num(int(c[0])) for c in data]

    hours = mdates.HourLocator(interval=4)
    dateFmt = mdates.DateFormatter('%H:%M')

    fig,ax = plt.subplots()
    dpi = fig.get_dpi()
    fig.set_size_inches(600/dpi, 200/dpi)

    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(dateFmt)
    ax.grid(which='major', linestyle='solid', color='grey')

    return dates, fig, ax

def plot_temp_graph(data,
                   output='graph-temp.png'):
    dates, fig, ax = plot_common(data)
    temps = [float(c[1]) for c in data]

    ax.plot(dates, temps, linewidth=4, color='black')
    ax.yaxis.set_major_locator(mticker.MultipleLocator(base=10.0))
    min_val = math.floor(min(temps)/10.0)*10
    max_val = math.ceil(max(temps)/10.0)*10
    ax.set_ylim([min_val, max_val])
    ax.set_ylabel('Temperature')

    plt.savefig(output, bbox_inches='tight')

def plot_pop_graph(data,
                   output='graph-pop.png'):
    dates, fig, ax = plot_common(data)
    pops = [float(c[1])*100 for c in data]
    ax.plot(dates, pops, linewidth=4, color='black')
    ax.set_ylim([0,100])
    ax.set_ylabel('% of Precipitation')

    plt.savefig(output, bbox_inches='tight')


