from datetime import datetime
from dateutil import parser
from dateutil.tz import tzutc

string = "2024-06-26T06:21:49.431Z"

dt = parser.parse(string)

date_str = dt.strftime('%a, %d %b %Y %H:%M:%S %Z')
naive_dt = datetime.strptime(date_str.split()[0] + ' ' + ' '.join(date_str.split()[1:-1]), '%a, %d %b %Y %H:%M:%S')  
aware_dt = naive_dt.replace(tzinfo=tzutc())
print(type(date_str))