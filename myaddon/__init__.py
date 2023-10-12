# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
#data.py
from .data import DataCalculator


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
