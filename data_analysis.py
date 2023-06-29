import os
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from nltk.tokenize import word_tokenize, MWETokenizer
from nltk.corpus import stopwords

def filter_data(df, title, level):
    tokenized_details = []
    df['tokenized_details'] = None
    df_filter = df.loc[df.title.str.contains(title, na=False, flags=re.IGNORECASE, regex=True)]
    df_filter = df_filter.loc[df.level.str.contains(level, na=False)].reset_index(drop=True)

    #iterrows() returns dataframe row copies. cannot edit details within function due to copywarnings.
    for idx, row in df_filter.iterrows():
        row_details = row.details.lower()
        row_details = word_tokenize(row_details)
        tokenizer = MWETokenizer([('computer', 'vision'), ('google', 'cloud')])
        row_details = tokenizer.tokenize(row_details)
        row_details = list(set(row_details))

        row_details = [word for word in row_details if word not in stopwords.words("english")]
        tokenized_details.append(row_details)

    return df_filter, tokenized_details

def barchart_keywords(df, keywords, title, head):
    num_jobs = len(df)
    keyword_count = pd.DataFrame(df.tokenized_details.sum()).value_counts().rename_axis("keywords").reset_index(name='counts')

    keyword_count['percentage'] = 100 * (keyword_count.counts / num_jobs)
    keyword_count = (keyword_count.loc[keyword_count.keywords.isin(keywords)]).head(head)
    ax = sns.barplot(data=keyword_count, x="keywords", y="percentage")
    ax.set(xlabel="", ylabel="Percentage likelihood to be in job listing (%)", title=title)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20)
    ax.yaxis.labelpad = 10

    plt.show()

# -------- main ----------------


df = pd.DataFrame()
# run the following 2 lines below ONCE
# nltk.download('punkt')
# nltk.download('stopwords')
path_to_data = "data/"
files = [os.path.join(path_to_data, file) for file in os.listdir(path_to_data)]

for file in files:
    temp_df = pd.read_csv(file, index_col=None)
    df = pd.concat([df, temp_df], ignore_index=True)

df.drop_duplicates(subset=["id"], inplace=True)
filtered_df, tokenized_details = filter_data(df, "Machine Learning|Deep Learning|ML", "Entry level")
filtered_df['tokenized_details'] = tokenized_details

machine_learning_keywords = ['tensorflow', 'keras', 'pytorch', 'python', 'nlp', 'scikit-learn', 'java',
                             'docker', 'azure', 'aws', 'kubernetes', 'computer_vision', 'opencv', 'sql',
                             'c++', 'c', 'cuda', 'spark', 'typescript', 'google_cloud', 'gpt', 'xgboost', 
                             'r', 'go', 'torch', 'gcp', 'jenkins', 'scala', 'git', 'devops', 'ci', 'react']

barchart_keywords(filtered_df, machine_learning_keywords, "Entry Level Machine Learning Skills", 10)
non_entry_levels = ['Mid-Senior level', 'Associate', 'Director', 'Executive', 'Internship']

for level in non_entry_levels:
    temp_df, token_details = filter_data(df, "Machine Learning", level)
    temp_df['tokenized_details'] = token_details
    filtered_df = pd.concat([filtered_df, temp_df], ignore_index=True)

barchart_keywords(filtered_df, machine_learning_keywords, "Experienced Machine Learning Skills", 10)
barchart_keywords(filtered_df, ['tensorflow', 'pytorch'], "TensorFlow versus PyTorch", 2)