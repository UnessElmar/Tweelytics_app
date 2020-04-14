import pandas as pd
from spacy.lang.fr.stop_words import STOP_WORDS
from wordcloud import WordCloud
import seaborn as sns
import pyLDAvis.gensim
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot

def tweets_history(df, from_instance, to_instance, by_param, n_hour):
    df = df[(df['date']>=from_instance) & (df['date']<=to_instance)]

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    bin_size=str(3600000)
    if by_param == 'H':
        if n_hour == 1:
            bin_size=str(3600000)   #1hr -> 3600000
        else:
            bin_size=str(n_hour * 3600000)   #1hr -> 3600000
    elif by_param == 'D':
        bin_size=str(24 * 3600000)   #1day -> 24 * 1hr
    tweets_time = df['date']

    trace = go.Histogram(
        x=tweets_time,
        xbins=dict(
            start=from_instance,
            end=to_instance,
            size= bin_size,
        ),
        marker=dict(
            color='blue'
        ),
        opacity=0.75
    )

    layout = go.Layout(
        title='Tweet Activity',
        height=450,
        xaxis=dict(
            title='Date - Time'
        ),
        yaxis=dict(
            title='Tweet Quantity'
        ),
        bargap=0.2,
    )

    return go.Figure(data=[trace], layout=layout)


def wordcould(model, nbr_topics):
    cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'

    cloud = WordCloud(stopwords=STOP_WORDS,
                      background_color='white',
                      width=2500,
                      height=1800,
                      max_words=10,
                      colormap='tab10',
                      color_func=lambda *args, **kwargs: cols[i],
                      prefer_horizontal=1.0)

    topics = model.show_topics(formatted=False)
    
    nbr_topics = int(nbr_topics)
    if nbr_topics % 2 == 0:
        fig, axes = plt.subplots(int(nbr_topics/2), 2, figsize=(18,20), sharex=True, sharey=True)

        for i, ax in enumerate(axes.flatten()):
            fig.add_subplot(ax)
            topic_words = dict(topics[i][1])
            cloud.generate_from_frequencies(topic_words, max_font_size=300)
            plt.gca().imshow(cloud)
            plt.gca().set_title('Topic ' + str(i+1), fontdict=dict(size=16))
            plt.gca().axis('off')
    else:
        fig, axes = plt.subplots(int(nbr_topics/2) + 1, 2, figsize=(18,20), sharex=True, sharey=True)
        for i, ax in enumerate(axes.flatten()):
            if i != nbr_topics:
                fig.add_subplot(ax)
                topic_words = dict(topics[i][1])
                cloud.generate_from_frequencies(topic_words, max_font_size=300)
                plt.gca().imshow(cloud)
                plt.gca().set_title('Topic ' + str(i+1), fontdict=dict(size=16))
                plt.gca().axis('off')
            else:
                fig.add_subplot(ax)
                plt.axis('off')

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.axis('off')
    plt.margins(x=0, y=0)
    plt.tight_layout()

    fig.savefig('data/temp/plot.jpg')



def ldaPlot(model, corpus):
    vis = pyLDAvis.gensim.prepare(model, corpus, dictionary=model.id2word)
    pyLDAvis.save_html(vis, 'data/temp/lda.html')