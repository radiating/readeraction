# readeraction
Insight Project: an automatic comment moderation tool for the New York Times
web url:  http://readeraction.press/demo

This project aims to filter NYTimes reader comments in 2 steps:
1) rid of inappropriate comments (swear words, derogatory comments)
2) ranking comments by their similarity index (by cosine similarity) to the article to decide whether the comments are on or off topic

<h2>I) Prerequisites</h2>

This project was written in Python 3.5.2.

New York Times API keys are expected. To get them, go to 1) https://developer.nytimes.com/article_search_v2.json) and 2) https://developer.nytimes.com/community_api_v3.json

The keys need to be supplied in the file: /readeraction/config_readeraction.py
nyt_key_article='...'
nyt_key_comment='...'

PostgreSQL is used. The connection to postgreSQL is expected to be in the format:
url='postgres://%s:%s@%s/%s' %(user,postgres_pw,host,dbname)
engine=create_engine(url)

where 'user' is 'postgres', 'host' is 'localhost', 'postgres_pw' is supplied in file: /readeraction/config_readeraction.py and 'dbname' is 'comment_tbl'.

<h2>II) Installing </h2>
Download all folders and files. Update the /readeraction/config_readeraction.py file with new API keys and PostgresSQL password.

<h2>III) Running code </h2>
- Go into folder which contains the 'run.py' script
- In Spyder (with Python 3), click 'Run File (F5)' on the 'run.py' script
- Open internet browser, enter address    http://127.0.0.1:5000/demo

<h2> IV) Results explanation </h2>
Go to blog: http://readeraction.press/blog
