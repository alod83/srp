from datetime import datetime
from datetime import timedelta

date_time = '2016-11-18 12:08:21'
epsilon = 90 # 1 minuto e mezzo
ps = 1800 # 30 minuti * 60 = 1800 secondi

sstep = ps - epsilon
estep = ps + epsilon
current_date = datetime.strptime(date_time,'%Y-%m-%d %H:%M:%S')
next_sdate = current_date + timedelta(seconds=sstep)
next_edate = current_date + timedelta(seconds=estep)
next_cdate = current_date + timedelta(seconds=ps)
print current_date
print next_sdate
print next_edate
print next_cdate
