from typing import List, Tuple
from aqt import mw

class DataCalculator:
    #start_day represents time closer to present
    def __init__(self, end_day: int, start_day=0):
        self.start_day = start_day
        self.end_day = end_day
        
    #returns a time in miliseconds in x days before
    def _interval_generator(self, days: int) -> int: 
        return (mw.col.sched.dayCutoff - 86400 * days) * 1000
    
    def query_stats(self, end_interval: int, start_interval: int):
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


        #start_day > end_day
    def retention_percent(self, end_day: int, start_day: int) -> str:
        start_interval = self._interval_generator(start_day)
        end_interval = self._interval_generator(end_day)
        full_stats = self.query_stats(end_interval, start_interval)
        flunked, passed = full_stats[0], full_stats[1]
        total  = flunked + passed
        try:
            calc = round(((passed / total) * 100), 2)
            temp = str(calc) + "%"
        except:
            temp = "N/A"
        result = temp
        return result
    
    #generates a list between the start and end days that were specified from earlier
    def generate_list(self) -> List[str]: 
        retentions = []
        for i in range(self.start_day + 1, self.end_day + 1):
            retention_per = self.retention_percent(i - 1, i)
            retentions.append(retention_per)
        return retentions