# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

import anki.stats
from .data import DataCalculator

#this injects code into the todayStats of CollectionStats from anki library
todayStats_old = anki.stats.CollectionStats.todayStats

# Types: 0 - new today; 1 - review; 2 - relearn; 3 - (cram?) [before the answer was pressed]
# "Learning" corresponds to New|Relearn. "Review" corresponds to Young|Mature.
# Ease: 1 - flunk button; 2 - second; 3 - third; 4 - fourth (easy) [which button was pressed]
# Intervals: -60 <1m -600 10m etc; otherwise days (>=21 is mature)
def _line_now(self, i, a, b, bold=True):
    colon = _(":")
    if bold:
        i.append(("<tr><td align=right>%s%s</td><td><b>%s</b></td></tr>") % (a,colon,b))
    else:
        i.append(("<tr><td align=right>%s%s</td><td>%s</td></tr>") % (a,colon,b))

def _lineTbl_now(self, i):
    return "<table>" + "".join(i) + "</table>"

def statList(self, lim, span):
    flunked, passed, passed_supermature, flunked_supermature, learned, relearned = self.col.db.first("""
    select
    sum(case when ease = 1 and type == 1 then 1 else 0 end), /* flunked */
    sum(case when ease > 1 and type == 1 then 1 else 0 end), /* passed */
    sum(case when ease > 1 and type == 1 and lastIvl >= 100 then 1 else 0 end), /* passed_supermature */
    sum(case when ease = 1 and type == 1 and lastIvl >= 100 then 1 else 0 end), /* flunked_supermature */
    sum(case when ivl > 0 and type == 0 then 1 else 0 end), /* learned */
    sum(case when ivl > 0 and type == 2 then 1 else 0 end) /* relearned */
    from revlog where id > ? """+lim, span)
    # ABOVE BUH?
    # you make this multi inequality thing
    # you are able to chain conditionals eg; WHERE (product_id > 3 AND product < 75)
    flunked = flunked or 0
    passed = passed or 0
    passed_supermature = passed_supermature or 0
    flunked_supermature = flunked_supermature or 0
    learned = learned or 0
    relearned = relearned or 0
    try:
        temp = "%0.1f%%" %(passed/float(passed+flunked)*100)
    except ZeroDivisionError:
        temp = "N/A"
    try:
        temp_supermature = "%0.1f%%" %(passed_supermature/float(passed_supermature+flunked_supermature)*100)
    except ZeroDivisionError:
        temp_supermature = "N/A"
    
    i = []
    _line_now(self, i, "True retention", temp)
    _line_now(self, i, "Supermature rate", temp_supermature)
    _line_now(self, i, "Passed reviews", passed)
    _line_now(self, i, "Flunked reviews", flunked)
    _line_now(self, i, "New cards learned", learned)
    _line_now(self, i, "Cards relearned", relearned)
    return _lineTbl_now(self, i)

def todayStats_new(self):
    lim = self._revlogLimit()
    if lim:
        lim = " and " + lim
    
    pastDay = statList(self, lim, (self.col.sched.dayCutoff-86400)*1000)
    pastWeek = statList(self, lim, (self.col.sched.dayCutoff-86400*7)*1000)
    
    if self.type == 0:
        period = 31; name = "Past month:"
    elif self.type == 1:
        period = 365; name = "Past year:"
    elif self.type == 2:
        period = float('inf'); name = "All time:"
    
    pastPeriod = statList(self, lim, (self.col.sched.dayCutoff-86400*period)*1000)
    
    return todayStats_old(self) + "<br><br><table style='text-align: center'><tr><td style='padding: 5px'>" \
        + "<span>Past day:</span>" + pastDay + "</td><td style='padding: 5px'>" \
        + "<span>Past week:</span>" + pastWeek + "</td><td style='padding: 5px'>" \
        + "<span>" + name + "</span>" + pastPeriod + "</td></tr></table>"




anki.stats.CollectionStats.todayStats = todayStats_new


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
    # get the number of cards in the current collection, which is stored in
    # the main window
    # s, e = 1, 0
    # seconds_day = 86400
    # startInterval = interval_generator(s)
    # endInterval = interval_generator(e)

    # myMethod = statListTest(startInterval, endInterval)
    # stat_list = []
    # for i in range(1, 32):
    #     retention = retention_percent(i, i - 1)
    #     stat_list.append(retention)
    # myMethodDebug = "regular myMethod " + str(s) + " " + str(e) + ": " + str(myMethod)
    # results = str([myMethodDebug, sum(list(myMethod)), stat_list, len(stat_list)])
    results = one_month_ret.generate_list()
    showInfo(str(results))

# create a new menu item, "test"
action = QAction("anki retention debug", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, debug)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
