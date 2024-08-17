import praw
from fpdf import FPDF
import os
from tqdm import tqdm

def remove_duplicates(posts_data):
    unique_posts = {}
    for post in posts_data:
        if post['url'] not in unique_posts:
            unique_posts[post['url']] = post
    return list(unique_posts.values())


def download_reddit_new_posts(posts_limit):
    client_id =  os.getenv("REDDIT_CLIENT_ID")
    # "jaFpZ0z_PWY2soXeGd0mYA"
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    # "Q0H60jSwf85iyRigV-3b9c7iUyxfdQ"
    # user_agent = os.getenv("USER_AGENT")
    # Set up the Reddit API client
    reddit = praw.Reddit(client_id=client_id,
                        client_secret=client_secret,
                        user_agent="test_bot")

    # Choose a subreddit
    subreddit = reddit.subreddit('f1visa')

    # Extract top posts
    top_posts = subreddit.new(limit=posts_limit)  # Adjust the limit as needed

    posts_data = []
    for post in tqdm(top_posts):
        post.comments.replace_more(limit=0)
        if post.num_comments > 5:
            top_comments = [comment.body for comment in post.comments]
            posts_data.append({
                'title': post.title,
                'content': post.selftext,
                'url': post.url,
                'comments': top_comments
            })
    # print (posts_data[0])
    return posts_data

def download_reddit_top_posts(posts_limit):
    client_id = "jaFpZ0z_PWY2soXeGd0mYA"
    client_secret = "Q0H60jSwf85iyRigV-3b9c7iUyxfdQ"
    # user_agent = os.getenv("USER_AGENT")
    # Set up the Reddit API client
    reddit = praw.Reddit(client_id=client_id,
                        client_secret=client_secret,
                        user_agent="test_bot")

    # Choose a subreddit
    subreddit = reddit.subreddit('f1visa')

    # Extract top posts
    top_posts = subreddit.top(limit=posts_limit)  # Adjust the limit as needed

    posts_data = []
    for post in tqdm(top_posts):
        post.comments.replace_more(limit=0)
        if post.num_comments > 5:
            top_comments = [comment.body for comment in post.comments]
            posts_data.append({
                'title': post.title,
                'content': post.selftext,
                'url': post.url,
                'comments': top_comments
            })
    # print (posts_data[0])
    return posts_data


def download_data_main(NUMBER_OF_POSTS):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Reddit Posts', ln=True, align='C')

        def add_post(self, title, content):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title.encode('latin1', 'replace').decode('latin1'), ln=True)
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 10, content.encode('latin1', 'replace').decode('latin1'))
            # self.set_text_color(0, 0, 255)
            # self.cell(0, 10, url, ln=True, link=url)
            # self.set_text_color(0, 0, 0)
            self.ln(10)

        def _sanitize_text(self, text):
            # Replace problematic characters with ASCII equivalents or remove them
            return text.encode('latin1', 'replace').decode('latin1')

        def add_comments(self, comments):
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, 'Comment of the post: ', ln=True)
            self.set_font('Arial', '', 10)
            for comment in comments:
                sanitized_comment = self._sanitize_text(comment)
                sanitized_comment = "New Comment: " + sanitized_comment
                self.multi_cell(0, 10, f"- {sanitized_comment}")
                self.ln(3)
            self.ln(10)

    top_posts_data = None
    new_posts_data = None
    total_posts_data = None
    try:
        top_posts_data = download_reddit_top_posts(NUMBER_OF_POSTS)
    except Exception as e:
        print ("Cannot download top reddit posts due to: ", e)

    try:
        new_posts_data = download_reddit_new_posts(NUMBER_OF_POSTS)
    except Exception as e:
        print ("Cannot download new reddit posts due to: ", e)

    total_posts_data = top_posts_data + new_posts_data
    try:
        total_posts_data = remove_duplicates(total_posts_data)
    except Exception as e:
        print ("remove_duplicates has failed due to", e)
    print ("Total number of data points: ", len(total_posts_data))
    list_urls = [i['url'] for i in total_posts_data]
    if len(list_urls)!=len(set(list_urls)):
        import pdb;pdb.set_trace()

    if total_posts_data is not None:
        pdf = PDF()
        pdf.add_page()
        for post in total_posts_data:
            pdf.add_post(f"Title of the post: {post['title']}", f"Body of the post: {post['content']}")
            pdf.add_comments(post['comments'])
        pdf.output('reddit_posts_top_new.pdf')
# download_data_main(5000)