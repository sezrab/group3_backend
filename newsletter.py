# WIP

import random
import smtplib
import fakemail
import webbrowser
import topic_classifier.paper_processor as pp
import firebase_manager
import article_database
import wordcloud
import datetime

uid = input("Enter your user ID: ")

user = firebase_manager.FirebaseUser(uid)

# get midnight of today
today = datetime.datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=0)

# get midnight of the day the user last received a newsletter
last_sent = today - datetime.timedelta(days=user.newsletter_period)
adb = article_database.ArticleDatabase()
interest_articles = adb.get_articles(sort=None, interests=user.interests,
                                     start_date=last_sent, stop_date=today)


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


general_articles = adb.get_articles(
    sort=None, interests=[], ignore_interests=True, start_date=last_sent, stop_date=today)
interest_wrapped = []
tag_count = tag_counter(general_articles)
for interest in user.interests:
    interest_wrapped.append((interest[0], tag_count.get(interest[0], 0)))

interest_wrapped = sorted(interest_wrapped, key=lambda x: x[1], reverse=True)
general_wrapped = nlp_wrapped(general_articles)

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
<img src="wordcloud.png" alt="Wordcloud" style="width: 100%; height: auto;">
<p>Hi {user.name},</p>
<p>Your NLP recap is here!</p>
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
<br>
<p>Happy reading!<br>
NLPress</p>
</body>
</html>
"""

try:
    server = smtplib.SMTP('localhost', 1025)
    server.set_debuglevel(1)
    fromaddr = "noreply@nlpress.com"
    toaddrs = ["samuelezraberry@gmail.com"]
    msg = ("From: %s\r\nTo: %s\r\n\r\n"
    % (fromaddr, ", ".join(toaddrs)))
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line:
            break
        msg = msg + line
    server.sendmail("noreply@nlpress.com", "samuelezraberry@gmail.com", out)
    print("Successfully sent email")
except smtplib.SMTPException:
    print("Error: unable to send email")

with open("newsletter.html", "w") as f:
    f.write(out)
webbrowser.open("newsletter.html")
