"""
Services for the contracts application.
"""
import datetime
import math
import jdatetime
from django.db.models import Max


def GregorianToShamsi(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        jDate = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  '%s-%s-%s' % (str(jDate.year), str(jDate.month), str(jDate.day))
    except Exception as e:
        return str(e)
    

def GregorianToShamsiShow(date):
    """
    Convert Gregorian date to Shamsi date for display.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        jDate = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  '%s-%s-%s' % (str(jDate.day), str(jDate.month), str(jDate.year))
    except Exception as e:
        return str(e)
    
        
def GregorianToShamsi1(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    y = (math.trunc(date.timestamp()) + 467066.53004084 - 0.641087919916919581508) / 365.24219878
    y1 = y - math.trunc(datetime.datetime.fromtimestamp(y))

    m = 1 + math.trunc(datetime.datetime.fromtimestamp(y1 / 0.084875187)) if (y1 <= 0.084875187 * 6) else \
        (7 + math.trunc(datetime.datetime.fromtimestamp((y1 - 0.084875187 * 6) / 0.082137278)) \
        if y1 <= (0.084875187 * 6 + 0.082137278 * 5) else 12)
                    
    mm = '0' + str(math.trunc(datetime.datetime.fromtimestamp(m))) if m < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(m)))

    d = math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 31)) + 1 if (m <= 6) else \
        math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 30 - 6)) + 1 if (m < 12) else \
        math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - 336)) + 1
                    
    dd = '0' + str(math.trunc(datetime.datetime.fromtimestamp(d))) if d < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(d)))
        
    result = str(math.trunc(datetime.datetime.fromtimestamp(y))) + '/' + mm + '/' + dd
    
    return result

