from datetime import datetime
from .models import DailyQuote

def get_daily_quote():
    quotes = DailyQuote.objects.all()
    if quotes.exists():
        day_of_year = datetime.now().timetuple().tm_yday
        return quotes[day_of_year % quotes.count()].quote
    return "No quote available for today."
