# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
#data.py
from .data import DataCalculator

import matplotlib.pyplot as plt
import numpy as np

def render(stats: DataCalculator) -> None:
    plt.style.use('_mpl-gallery')
    end_day = stats.get_period()[0]
    x = 0.5 + np.range(end_day)
    y = stats.generate_list()
    fig, ax = plt.subplots()

    ax.bar(x, y, width=1, edgecolor="white", linewidth=0.7)

    ax.set(xlim=(0, 100), xticks=np.arange(1, 100),
       ylim=(0, 100), yticks=np.arange(1, 100))

    plt.show()

#tester method from Heatmap Review
def find_cards_reviewed_between(self, start_date: int, end_date: int):
    # select from cards instead of just selecting uniques from revlog
    # in order to exclude deleted cards
    return mw.col.db.list(  # type: ignore
        "SELECT id FROM cards where id in "
        "(SELECT cid FROM revlog where id between ? and ?)",
        start_date,
        end_date,
    )

one_month_ret = DataCalculator(31, 0)
def debug() -> None:
    results = one_month_ret.generate_list()
    showInfo(str(results))

# create a new menu item, "test"
action = QAction("anki retention debug", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, debug)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
