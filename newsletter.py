# WIP

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from pathlib import Path
import random
import smtplib
import topic_classifier.paper_processor as pp
import firebase_manager
import article_database
import wordcloud
import datetime


uid = input("Enter your user ID: ")

user = firebase_manager.FirebaseUser(uid)
user_read_articles = firebase_manager.FirebaseManager().get_read_articles(uid)

# get midnight of today
today = datetime.datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=0)

# get midnight of the day the user last received a newsletter
last_sent = today - datetime.timedelta(days=user.newsletter_period)
adb = article_database.ArticleDatabase()
interest_articles = adb.get_articles(sort=None, interests=user.interests,
                                     start_date=last_sent, stop_date=today)


# how many articles has the user read between start and end?
def no_of_articles_read(start, end): 
    articles_counter = 0
    for article_date in user_read_articles.values():
        if start < article_date and end >= article_date:
            articles_counter += 1   # articles read this newsletter period
    return articles_counter

# finds the first n most popular tags and works out what n is
def nlp_wrapped(articles):
    tags = tag_counter(articles)
    tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    out = []
    c = 0
    for tag, count in tags:
        if count > 0.5 * tags[0][1]:
            c += 1
            if c > 5:
                break
            out.append((tag, count))
            # print(f"  {tag} ({count} articles)")
    return out


def tag_counter(articles):
    tag_counter = {}
    for article, score in articles:
        for tag, _ in article.tags:
            tag_counter[tag] = tag_counter.get(tag, 0) + 1

    return tag_counter

# articles read since last newsletter (between now and last newsletter sent)
read_since_last_newsletter = no_of_articles_read(datetime.datetime.now() - datetime.timedelta(days=user.newsletter_period), datetime.datetime.now())

# articles read since last last newsletter
read_since_last_last_newsletter = no_of_articles_read(datetime.datetime.now() - datetime.timedelta(days=2*user.newsletter_period), datetime.datetime.now() - datetime.timedelta(days=user.newsletter_period))

if read_since_last_last_newsletter - read_since_last_newsletter > 0:
    reading_summary = f"Well done! You've viewed {read_since_last_last_newsletter - read_since_last_newsletter} more than last time!. Keep reading!"
elif read_since_last_last_newsletter - read_since_last_newsletter < 0:
    reading_summary = f"You've viewed {read_since_last_newsletter - read_since_last_last_newsletter} less than last time!. Keep reading!"
else:
    reading_summary = "You're reading pattern has stayed consistent since last time! You've read the same amount of articles as last time"


# articles unread
general_articles = adb.get_articles(
    sort=None, interests=[], ignore_interests=True, start_date=last_sent, stop_date=today)
interest_wrapped = []
tag_count = tag_counter(general_articles)
for interest in user.interests:
    interest_wrapped.append((interest[0], tag_count.get(interest[0], 0)))

interest_wrapped = sorted(interest_wrapped, key=lambda x: x[1], reverse=True)
general_wrapped = nlp_wrapped(general_articles)


def suggest_tags(start, end):
    suggest_tag = []
    for article_date in user_read_articles.values():
        if start < article_date and end >= article_date:
            read_tags = tag_counter(user_read_articles)
            for tag in read_tags:
                for interest in user.interests:
                    if tag[0] != interest[0]:
                        suggest_tag.append(tag)
    suggest_tag_wrapped = sorted(interest_wrapped, key=lambda x: x[1], reverse=True)
    return suggest_tag_wrapped


big_abstract = ""
for article, score in interest_articles:
    big_abstract += article.abstract
if big_abstract == "":
    print("No articles found for your interests in the past",
          user.newsletter_period, "days.")
    exit()
wc = wordcloud.WordCloud(
    background_color="rgba(255, 255, 255, 0)", mode="RGBA", width=1300, height=200, collocations=False, colormap="viridis")
wc.generate_from_frequencies(
    pp.tf(big_abstract))
wc.to_file("wordcloud.png")


mustread = []
interest_articles = interest_articles[:10]
c = 0
for article, score in interest_articles[:10]:
    c += 1
    date_nice = article.published.strftime("%B %d, %Y")
    mustread.append(article)

indistinct_summary = [
    f"It's been an interesting {user.newsletter_period} days.",
    "NLP has been busy as always.",
    f"The last {user.newsletter_period} days have seen some interesting discussion in the NLP community.",
    "NLP has been active lately, and the chances are you have some catching up to do.",
    "NLP has had a busy week. Haven't we all?",
]
random_summary = random.choice(indistinct_summary)

out = f"""
<html>
<head>
<style>
body {"{"}
  font-family: Arial, sans-serif;
{"}"}
</style>
</head>
<body>
<img src="cid:image1" alt="Wordcloud" style="width: 100%; height: auto;">
<p>Hi {user.name},</p>
<p>Your NLP recap is here!</p>
<p>In the past {user.newsletter_period} days, you've viewed {read_since_last_newsletter} articles. Well done!</p>
<p>{read_}</p>
<p>Here are your <b>must read</b> papers from the past {user.newsletter_period} days.</p>
<ol>
{"".join([f'<li><a href="{article.url}" target="_blank">{article.title}</a></li>' for article in mustread])}
</ol>
<p>{random_summary} <br>
<p>Over this period, {len(general_wrapped)} topics thrived:</p>
<ul>
{"".join([f'<li>{tag}, with {count} articles.</li>' for tag, count in general_wrapped])}
</ul>
<p>Of your interests, the most active were:</p>
<ul>
{"".join([f'<li>{tag} ({count} articles)</li>' for tag, count in interest_wrapped])}
</ul>
<p>Here are some sugguested interests from the articles you have read:</p>
<ul>
{"".join([f'<li>{tag} ({count} articles)</li>' for tag, count in suggest_tag_wrapped])}
</ul>
<br>
<p>Happy reading!<br>
NLPress</p>
</body>
</html>
"""


creds = str(Path.home()) + "/nlpresscrds"

if os.path.exists(creds):
    with open(creds, 'r') as f:
        username,password = [line.strip() for line in f.readlines()]
else:
    print("No password file found. Please create a file at " + creds + " containing your email password.")
    exit()

img = open('wordcloud.png', 'rb').read() # read bytes from file
# Create a multipart message container
msg = MIMEMultipart()
msg['From'] = "noreply@nlpress.com"
msg['To'] = user.email
msg['Subject'] = "Your NLP Recap"
image = MIMEImage(img, name='wordcloud.png')
image.add_header('Content-ID', '<image1>')
msg.attach(image)
msg.attach(MIMEText(out, 'html'))

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
    smtp_server.login(username, password)
    smtp_server.send_message(msg)
