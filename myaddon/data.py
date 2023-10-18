from typing import List, Tuple
from aqt import mw

class DataCalculator:
    #start_day represents time closer to present
    def __init__(self, end_day: int, start_day=0):
        self._start_day = start_day
        self._end_day = end_day
        
    #returns a time in miliseconds in x days before
    def _interval_generator(self, days: int) -> int: 
        return (mw.col.sched.dayCutoff - 86400 * days) * 1000
    
    def query_stats(self, end_interval: int, start_interval: int) -> Tuple[int]:
        flunked, passed, passed_supermature, flunked_supermature, relearned, learned = mw.col.db.first(
        f"""select
        sum(case when ease = 1 and type == 1 then 1 else 0 end), /* flunked */
        sum(case when ease > 1 and type == 1 then 1 else 0 end), /* passed */
        sum(case when ease > 1 and type == 1 and lastIvl >= 100 then 1 else 0 end), /* passed_supermature */
        sum(case when ease = 1 and type == 1 and lastIvl >= 100 then 1 else 0 end), /* flunked_supermature */
        sum(case when ivl > 0 and type == 2 then 1 else 0 end), /* relearned */
        sum(case when ivl > 0 and type == 0 then 1 else 0 end) /* learned */
        from revlog where id between {start_interval} and {end_interval}""")
        return (flunked, passed, passed_supermature, flunked_supermature, relearned, learned)

    def retention_percent(self, end_day: int, start_day: int) -> str:
        start_interval = self._interval_generator(start_day)
        end_interval = self._interval_generator(end_day)
        full_stats = self.query_stats(end_interval, start_interval)
        flunked, passed = full_stats[0], full_stats[1]
        try:
            total  = flunked + passed
            calc = round(((passed / total) * 100), 2)
            temp = str(calc) + "%"
        except TypeError:
            temp = "No cards studied yet"
        except ZeroDivisionError:
            temp = "Zero division error"
        result = temp
        return result
    
    def formatter(self, stat: int) -> str:
        if stat == -1:
            return "N/A"
        else:
            return str(stat) + "%"
    
    #generates a list between the start and end days that were specified from earlier
    def generate_list(self) -> List[str]: 
        retentions = []
        for i in range(self._start_day + 1, self._end_day + 1):
            retention_per = self.retention_percent(i - 1, i)
            retentions.append(retention_per)
        return retentions
    
    def get_period(self) -> Tuple(int, int):
        return self._start_day, self.end_day