# WIP

import topic_classifier.paper_processor as pp
import firebase_manager
import article_database
import wordcloud
import datetime

uid = "EkGSwlKgaaNkiz8fr4LLOd9YCno1"

user = firebase_manager.FirebaseUser(uid)

# get midnight of today
today = datetime.datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=0)

# get midnight of the day the user last received a newsletter
last_sent = today - datetime.timedelta(days=user.newsletter_period)
print()
print("-"*40)
print("To:", user.email)
print("Subject: Your NLP newsletter")
print()
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

wc = wordcloud.WordCloud(
    background_color="rgba(255, 255, 255, 0)", mode="RGBA", width=1300, height=200, collocations=False, colormap="viridis")
# toks = pp.tokenize(big_abstract)
# big_abstract = " ".join(toks)
wc.generate_from_frequencies(
    pp.tf(big_abstract))
wc.to_file("wordcloud.png")

print(f"Of your interests, the {
      len(interest_wrapped)} most active topics were:")

for tag, count in interest_wrapped:
    print(f"  {tag} ({count} articles)")

print()

print(f"Overall this period, the {
      len(general_wrapped)} most active topics were:")
for tag, count in general_wrapped:
    print(f"  {tag} ({count} articles)")
print()

print(f"And here are your must read papers from the past {
      user.newsletter_period} days."),

interest_articles = interest_articles[:10]
c = 0
for article, score in interest_articles[:10]:
    c += 1
    date_nice = article.published.strftime("%B %d, %Y")
    print(str(c)+".", article.title)
print()
print()
print("Happy reading!")
print("NLPress")
print("-"*40)
