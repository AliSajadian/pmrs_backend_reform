import datetime
import math
import jdatetime


def gregorian_to_shamsi(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        j_date = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  f"{str(j_date.year)}, {str(j_date.month)}, {str(j_date.day)}"
    except (ValueError, AttributeError, TypeError) as e:
        return str(e)


def gregorian_to_shamsi_show(date):
    """
    Convert Gregorian date to Shamsi date for display.
    """
    # gregorian_date = jdatetime.date(1400,5,24).togregorian()
    try:
        j_date = jdatetime.date.fromgregorian(day=date.day,month=date.month,year=date.year)
        return  f"{str(j_date.day)}, {str(j_date.month)}, {str(j_date.year)}"
    except (ValueError, AttributeError, TypeError) as e:
        return str(e)

        
def gregorian_to_shamsi1(date):
    """
    Convert Gregorian date to Shamsi date.
    """
    y = (math.trunc(date.timestamp()) + 467066.53004084 - 0.641087919916919581508) / 365.24219878
    y1 = y - math.trunc(datetime.datetime.fromtimestamp(y))

    m = 1 + math.trunc(datetime.datetime.fromtimestamp(y1 / 0.084875187)) \
         if (y1 <= 0.084875187 * 6) else \
           (7 + math.trunc(datetime.datetime.fromtimestamp((y1 - 0.084875187 * 6) / 0.082137278)) \
           if y1 <= (0.084875187 * 6 + 0.082137278 * 5) else 12)

    mm = '0' + str(math.trunc(datetime.datetime.fromtimestamp(m))) if m < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(m)))

    d = math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 31)) + 1 \
        if (m <= 6) else \
          math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - (m - 1) * 30 - 6)) + 1 \
          if (m < 12) else \
            math.trunc(datetime.datetime.fromtimestamp(y1 * 365.24219878 - 336)) + 1

    dd = '0' + str(math.trunc(datetime.datetime.fromtimestamp(d))) if d < 10 else \
        str(math.trunc(datetime.datetime.fromtimestamp(d)))

    result = str(math.trunc(datetime.datetime.fromtimestamp(y))) + '/' + mm + '/' + dd

    return result

