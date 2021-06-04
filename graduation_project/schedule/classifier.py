from apscheduler.schedulers.background import BackgroundScheduler
from feed_api.models import Feed, Comment, FeedVote, Report, CommentLike, CommentReport
from datetime import datetime, timedelta, timezone
import joblib

today = datetime.now(tz=timezone.utc)
start_date = today - timedelta(days=1)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(getFeeds, "interval", hours=4, id="feed_001", replace_existing=True)
    scheduler.add_job(getComments, "interval", hours=4, id="comment_001", replace_existing=True)
    scheduler.start()
    
def getFeeds():
    for feed in Feed.objects.filter(postedDate__range=[start_date, today]):
        upvote = FeedVote.objects.filter(feed=feed, vote=1).count()
        downvote = FeedVote.objects.filter(feed=feed, vote=1).count()
        report = Report.objects.filter(feed=feed).count()
        
        prediction = predictFeed(upvote, downvote, report) 
        if int(prediction) == 1:
            feed.isSpam = True
            feed.save()

def getComments():
    for comment in Comment.objects.filter(postedDate__range=[start_date, today]):
        like = CommentLike.objects.filter(comment=comment).count()
        report = CommentReport.objects.filter(comment=comment).count()
        
        prediction = predictComment(like, report)
        if int(prediction) == 1:
            comment.isSpam = True
            comment.save()
    
def predictFeed(upvote, downvote, report):
    loaded_rf = joblib.load("graduation_project/schedule/feed_classifier_model.joblib")
    return loaded_rf.predict([[upvote, downvote, report]])[0]

def predictComment(like, report):
    loaded_rf = joblib.load("graduation_project/schedule/comment_classifier_model.joblib")
    return loaded_rf.predict([[like, report]])[0]
    