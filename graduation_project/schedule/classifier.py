from apscheduler.schedulers.background import BackgroundScheduler
from feed_api.models import Feed, Comment
from datetime import datetime, timedelta, timezone

today = datetime.now(tz=timezone.utc)
start_date = today - timedelta(hours=4)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(getFeeds, "interval", hours=4, id="feed_001", replace_existing=True)
    scheduler.add_job(getComments, "interval", hours=4, id="comment_001", replace_existing=True)
    scheduler.start()
    
def getFeeds():
    print("\nScheduler called and ", Feed.objects.filter(postedDate__range=[start_date, today]))

def getComments():
    print("\nScheduler 2 called and ", Comment.objects.filter(postedDate__range=[start_date, today]))