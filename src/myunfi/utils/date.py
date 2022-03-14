import calendar

from dateutil import parser


def last_thursday(year, month):
    return last_of_month(year, month, weekday=calendar.THURSDAY)


def last_saturday(year, month):
    return last_of_month(year, month, weekday=calendar.SATURDAY)


def last_friday(year, month):
    return last_of_month(year, month, weekday=calendar.FRIDAY)


def last_of_month(year, month, weekday=calendar.SUNDAY):
    """
    Get the last day of a month
    """
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    last_day = [day for week in monthcal for day in week if
                day.weekday() == weekday and
                day.month == month][-1]
    return last_day


def fuzzy_date(datestr, verbose=False):
    dateobj = None
    for word in datestr.replace('_', ' ').replace('-', ' ').strip(' ').split(' '):
        try:
            dateobj = parser.parse(word)
            fname = datestr.lower()
            if dateobj.strftime('%B').lower() in fname \
                    or dateobj.strftime('%b').lower() in fname:
                if verbose:
                    print('{word} matched to {month:%B}'.format(
                        word=word, month=dateobj))
                break
        except ValueError:
            pass
    return dateobj


