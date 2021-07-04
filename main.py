import argparse
import json
from calendar import monthrange
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

END = datetime.today()
plt.ioff()

if __name__ == "__main__":

    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--history_file",
        default="history.json",
        help="History JSON file export from Chrome (deafult: history.json)",
    )
    parser.add_argument(
        "-s",
        "--start",
        default="2021-05-12",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
        help="Start date in %%Y-%%m-%%d format (default: 2021-05-12)",
    )
    args = parser.parse_args()

    # Load data
    with open(args.history_file) as f:
        hist = json.load(f)

    # Organize history entry into hierarchal dictionary
    metrics = {
        month: {
            day: {hour: [] for hour in range(24)}
            for day in range(1, monthrange(args.start.year, month)[1] + 1)
        }
        for month in range(args.start.month, END.month + 1)
    }
    for entry in hist:
        dt = datetime.fromtimestamp(entry["visitTime"] / 1000)
        if args.start <= dt and dt <= END:
            metrics[dt.month][dt.day][dt.hour].append(entry)

    # Calculate entry for each unit (hour)
    metrics_len = []
    extra_axes = args.start.weekday() + 1
    curs = args.start - timedelta(days=extra_axes)
    while curs <= END:
        for hour in range(24):
            length = len(metrics[curs.month][curs.day][hour])
            metrics_len.append(
                {
                    "date": f"{curs.month}/{curs.day}",
                    "hour": hour,
                    "activity": length,
                }
            )
        curs += timedelta(days=1)

    # plot in calendar style
    df = pd.DataFrame.from_dict(metrics_len)
    max_height = (max(df["activity"]) // 50 + 1) * 50
    grid = sns.FacetGrid(
        df,
        col="date",
        hue="date",
        col_wrap=7,
        sharex=False,
        sharey=False,
        legend_out=False,
    )
    grid.set(
        xticks=[0, 6, 12, 18, 24],
        yticks=range(0, max_height + 1, 50),
        xlim=(-1, 24),
        ylim=(0, max_height),
    )
    grid.set_xlabels("")
    grid.set_ylabels("")
    grid.map(plt.plot, "hour", "activity", marker="o")
    grid.fig.subplots_adjust(wspace=0.5)
    for axe in grid.fig.axes[:extra_axes]:
        axe.set_visible(False)

    # Export Figure
    grid.savefig("Full.png")
    curs = args.start
    for axe in grid.fig.axes[extra_axes:]:
        extent = axe.get_window_extent().transformed(
            grid.fig.dpi_scale_trans.inverted()
        )
        grid.fig.savefig(
            f"{curs.strftime('%m%d')}.png", bbox_inches=extent.expanded(1.4, 1.2)
        )
        curs += timedelta(days=1)
