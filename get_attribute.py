'''
    This file contains our replication package, providing the procedure for retrieval the variables used in the paper.
'''
import warnings
warnings.simplefilter('ignore')
import fasttext
import datetime
import csv
import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension ## pip install py_gfm
import re
import string
from nltk.stem import PorterStemmer

# Filtering issue
def filter_issue(issue:dict) -> bool:
    '''
        If the issue satisfies any of the conditions mentioned below, the function will return False; otherwise, it will return True:
            1. The issue is written in a non-English language.
            2. The issue is closed within a very short period of time.
            3. The issue is submitted by bots.
            4. The issue is invalid.
    '''
    # regarding 1
    fasttext_model = fasttext.load_model("./fasttext-model.bin")
    if issue["body"] == None: issue["body"] = ""
    text = issue['body'].replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    lang = fasttext_model.predict(text, 1)[0]
    if lang[0] != "__label__en":
        return False
    
    # regarding 2
    created_at = issue["created_at"] # 2022-01-13T10:59:31Z
    closed_at = issue["closed_at"]
    assert created_at != None and closed_at != None; "error: created_at or closed_at is None"
    closedtime = (datetime.datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ") - datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
    if closedtime < 30:
        return False
    
    # regarding 3 (similar to is_bot function)
    user_login = issue["user"]["login"]
    if 'bot' == re.sub('[^a-z]', '', user_login)[-3:]:
        return False
    with open("./groundtruthbots.csv", "r") as f:
        reader = csv.reader(f)
        bots = set([row[0] for row in reader if row[2]=="Bot"])
    if user_login in bots:
        return False
    
    # regarding 4
    labels = [i["name"].lower() for i in issue["labels"]]
    for label in labels:
        if "invalid" in label or "duplicate" in label:
            return False
    return True

# Check wether bug or not
def is_bug(issue:dict) -> bool:
    '''
        If the issue is related to a bug, the function will return True; otherwise, it will return False. 
        This function is intended to be used with the issue passed through the filter_issue function.
    '''
    labels = [i["name"].lower() for i in issue["labels"]]
    for label in labels:
        for tag in ["bug", "crash", "defect","regression","unexpected behaviour"]:
            if (tag in label) and not("not" in label):
                return True
    return False

# DescriptionWords
def get_description_words(issue:dict) -> list:
    '''
        This function returns the words in the description of the issue.
    '''
    if issue["body"] == None: issue["body"] = ""
    text = issue['body']
    text = re.sub('\(', ':', text)
    text = re.sub('\)', ':', text)
    pattern = re.compile("[[a-z0-9\-_ ]+]:https://user-images\.githubusercontent\.com/.*?(png|jpg|jpeg|gif|mp4|mov)")
    text = pattern.sub('', text)
    pattern = re.compile("https?://.*?(:|\s)")
    text = pattern.sub('', text)
    try:
        htmlText = markdown.markdown(text,extensions=[GithubFlavoredMarkdownExtension()])
    except: 
        print("Error: Unable to convert markdown to html.")
    htmlText = re.sub('\n+', ' ', htmlText)
    htmlText = re.sub('^\n', ' ', htmlText)
    htmlText = re.sub('\n$', ' ', htmlText)
    pattern = re.compile("<code>(.*?)</code>")
    htmlText = pattern.sub(' ', htmlText)
    pattern = re.compile("<table>(.*?)</table>")
    htmlText = pattern.sub(' ', htmlText)
    pattern = re.compile("<(.*?)>")
    text = pattern.sub(' ', htmlText)
    text = re.sub(' +', ' ', text)

    words = re.findall('[a-z]+', text.lower())

    # remove stop words
    stopWords = set(list(string.ascii_lowercase)
                    +['i','me','my','myself','we','our','ours','ourselves','you',"you're","you've","you'll","you'd",'your','yours', 'yourself','yourselves',
                        'he','him','his','himself','she',"she's",'her','hers','herself','it', "it's",'its','itself','they','them','their','theirs','themselves',
                        'this','that',"that'll",'these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing',
                        'a','an','the','and','but', 'or','because','as','until','while','of','at','by','for','with','about','against','between','into', 'through','during','before','after',
                        'above','below','to','from','up','down','in','out','on','off','over','under','again', 'further','then','once','here','there','all','any','both','each','few','more','most',
                        'other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don',"don't",'should',"should've",'now','d','ll',
                        'm','o','re','ve','y','ain','aren',"aren't",'couldn',"couldn't",'didn',"didn't",'doesn',"doesn't",'hadn',"hadn't",'hasn',"hasn't",'haven',"haven't",'isn',"isn't",
                        'ma','mightn',"mightn't",'mustn',"mustn't",'needn',"needn't",'shan',"shan't",'shouldn',"shouldn't",'wasn',"wasn't",'weren',"weren't",'won',"won't",'wouldn',"wouldn't"])
    words = [word for word in words if word not in stopWords]
    words = [word for word in words if not any(chr.isdigit() for chr in word)]

    # stemming
    ps = PorterStemmer()
    words = [ps.stem(word) for word in words]
    
    return words

# DescriptionLength
def get_description_length(issue:dict) -> int:
    '''
        This function returns the length of the description of the issue.
    '''
    if issue["body"] == None: issue["body"] = ""
    text = issue['body']
    text = re.sub('\(', ':', text)
    text = re.sub('\)', ':', text)
    pattern = re.compile("[[a-z0-9\-_ ]+]:https://user-images\.githubusercontent\.com/.*?(png|jpg|jpeg|gif|mp4|mov)")
    text = pattern.sub('', text)
    pattern = re.compile("https?://.*?(:|\s)")
    text = pattern.sub('', text)
    try:
        htmlText = markdown.markdown(text,extensions=[GithubFlavoredMarkdownExtension()])
    except: 
        print("Error: Unable to convert markdown to html.")
    htmlText = re.sub('\n+', ' ', htmlText)
    htmlText = re.sub('^\n', ' ', htmlText)
    htmlText = re.sub('\n$', ' ', htmlText)
    pattern = re.compile("<code>(.*?)</code>")
    htmlText = pattern.sub(' ', htmlText)
    pattern = re.compile("<table>(.*?)</table>")
    htmlText = pattern.sub(' ', htmlText)
    pattern = re.compile("<(.*?)>")
    text = pattern.sub(' ', htmlText)
    text = re.sub(' +', ' ', text)

    words = re.findall('[a-z]+', text.lower())
    return len(words)

# Comments
def get_comments(issue:dict) -> int:
    '''
        This function returns the number of comments in the issue.
    '''
    comments = len(issue["comments_dict"].keys())
    if comments == 0: return 0

    for key in issue["comments_dict"].keys():
        if key == "Error": continue
        comment = issue["comments_dict"][key]
        if is_bot(comment["user"]["login"]):
            comments -= 1

    return comments

# FirstCommentTime
def get_firstCommentTime(issue:dict) -> float:
    '''
        This function returns the time difference between the first comment and the issue creation time.
    '''
    if get_comments(issue) == 0:
        return None
    else:
        oldest = None
        for key in issue["comments_dict"].keys():
            if key == "Error": continue ## Comments are unavailable.
            comment = issue["comments_dict"][key]
            if is_bot(comment["user"]["login"]):
                continue
            comment_num = int(re.findall(r'\d+', key)[0])
            if oldest == None:
                oldest = comment_num
            else:
                if oldest > comment_num:
                    oldest = comment_num

        firstCommentTime = datetime.datetime.strptime(issue["comments_dict"][str(oldest)+"th comment"]["created_at"], '%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(issue["created_at"], '%Y-%m-%dT%H:%M:%SZ')
        firstCommentTime = firstCommentTime.total_seconds()/(3600*24)
        return firstCommentTime

# LastCommentTime
def get_lastCommentTime(issue:dict) -> float:
    '''
        This function returns the time difference between the last comment and the issue creation time.
    '''
    if get_comments(issue) == 0:
        return None
    else:
        newest = None
        for key in issue["comments_dict"].keys():
            if key == "Error": continue ## Comments are unavailable.
            comment = issue["comments_dict"][key]
            if is_bot(comment["user"]["login"]):
                continue
            comment_num = int(re.findall(r'\d+', key)[0])
            if newest == None:
                newest = comment_num
            else:
                if newest < comment_num:
                    newest = comment_num
        if newest != None:
            lastCommentTime = datetime.datetime.strptime(issue["comments_dict"][str(newest)+"th comment"]["created_at"], '%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(issue["created_at"], '%Y-%m-%dT%H:%M:%SZ')
            lastCommentTime = lastCommentTime.total_seconds()/(3600*24)
            return lastCommentTime
        else:
            return None

# Participants
def get_participants(issue:dict) -> int:
    '''
        This function returns the number of participants in the issue, except for the issue creator.
    '''
    participants = [issue["user"]["login"]]
    for key in issue["comments_dict"].keys():
        if key == "Error": continue
        if is_bot(issue["comments_dict"][key]["user"]["login"]):
            continue
        if not(issue["comments_dict"][key]["user"]["login"] in participants):
            participants.append(issue["comments_dict"][key]["user"]["login"])

    return len(participants) - 1

# ClosedTime
def get_closedTime(issue:dict) -> float:
    '''
        This function returns the time difference between the issue creation time and the issue closing time.
    '''
    closedTime = datetime.datetime.strptime(issue["closed_at"], '%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(issue["created_at"], '%Y-%m-%dT%H:%M:%SZ')
    closedTime = closedTime.total_seconds()/(3600*24)
    return closedTime

def is_bot(user_login:str) -> bool:
    '''
        This function returns True if the user is a bot; otherwise, it returns False.
    '''
    if 'bot' == re.sub('[^a-z]', '', user_login)[-3:]:
        return True
    with open("./groundtruthbots.csv", "r") as f:
        reader = csv.reader(f)
        bots = set([row[0] for row in reader if row[2]=="Bot"])
    if user_login in bots:
        return True
    else:
        return False

if __name__ == "__main__":
    sample_issue = {"user":{"login":"reporter"},
             "body":"Hello! In m_fonts.cpp:330 (tag handler for BIG and SMALL)\r\n```\r\nint oldsize = m_WParser->GetFontSize();\r\nint sz = (tag.GetName() == wxT(\"BIG\")) ? +1 : -1;\r\nm_WParser->SetFontSize(sz);\r\n```\r\nThat results in SetFontSize(1) for BIG and SetFontSize(-1) for SMALL.\r\nLooking at SetFontSize() in winpars.cpp:535:\r\n```\r\nif (s < 1)\r\n    s = 1;\r\nelse if (s > 7)\r\n    s = 7;\r\nm_FontSize = s;\r\n```\r\nso both 1 and -1 result in m_FontSize = 1, the smallest font.Best Regards:\r\nZsolt",
             "labels":[{"name":"bug"}],
             "created_at":"2022-01-10T10:00:00Z", 
             "closed_at":"2022-01-13T10:00:00Z", 
             "comments":2, 
             "comments_dict":{"1th comment":{"created_at":"2022-01-11T10:00:00Z", "user": {"login":"reporter"}}, 
                              "2th comment":{"created_at":"2022-01-13T09:00:00Z", "user": {"login":"developer"}}}}
    print(f"{filter_issue(sample_issue) = }")
    print(f"{is_bug(sample_issue) = }")
    print(f"{get_description_words(sample_issue) = }")
    print(f"{get_description_length(sample_issue) = }")
    print(f"{get_comments(sample_issue) = }")
    print(f"{get_firstCommentTime(sample_issue) = }")
    print(f"{get_lastCommentTime(sample_issue) = }")
    print(f"{get_participants(sample_issue) = }")
    print(f"{get_closedTime(sample_issue) = }")
