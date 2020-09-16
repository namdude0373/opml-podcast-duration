import opml
import feedparser
from datetime import datetime, timedelta
import csv


# import matplotlib.pyplot as plt  # this can be added if you want to have Python create a graph


def opmltorss(opml_file):
    podcasts = opml.parse(opml_file)
    podcastlist = []
    for i in range(len(podcasts[0])):  # may need to remove one item as there is a header
        feed = feedparser.parse(podcasts[0][i].xmlUrl)
        for episode in feed.entries:
            try:
                episodeduration = episode.itunes_duration
                if episodeduration == 0:
                    raise AttributeError  # essentially skipping down to the next line
            except AttributeError:  # if the episode duration is missing or listed as zero
                episodeduration = input(
                    'What is the episode duration (in seconds) for episode {} in {}?'.format(episode.title,
                                                                                             podcasts[0][i].text))
            podcastlist.append([podcasts[0][i].text, episode.title, episode.published, episodeduration])
    with open('podcastlist.csv', 'w', newline='') as file:
        for p in podcastlist:
            csv.writer(file).writerow(p)
    return podcastlist


def stringtodatetime(list_in):  # note that it is possible to retain the time in function, just need to change string
    for row in list_in:
        if row[2][-1].isalpha():
            row[2] = datetime.strptime(row[2][5:-13], '%d %b %Y')  # for the timestamp with a time zone
        else:
            row[2] = datetime.strptime(row[2][5:-15], '%d %b %Y')  # for timestamps that use 24 hour time


def sumduration(list_in):
    list_in.sort(key=lambda x: x[2])  # get minimum date on top
    currentdate = list_in[0][2]
    maxdate = list_in[-1][2]  # last item in sorted list will be the biggest
    datelist = []
    durationlist = []
    combinedlist = []
    while currentdate <= (maxdate + timedelta(days=1)):
        totaltime = 0
        for row in list_in:
            if row[2] == currentdate:
                if row[3].count(':') > 1:  # hour:min:sec time format
                    adjtime = row[3].split(':')
                    duration = (int(adjtime[0]) * 3600) + (int(adjtime[1]) * 60) + int(adjtime[2])
                elif ':' in row[3]:  # hour:min time format
                    adjtime = row[3].split(':')
                    duration = (int(adjtime[0]) * 60) + int(adjtime[1])
                else:  # simple format (seconds only)
                    duration = row[3]
                if duration == 0:  # podcast episode should always be above one, this is a redundant error check
                    raise Exception()
                totaltime += int(duration) / 3600  # seconds to hours conversion
        datelist.append(currentdate)
        durationlist.append(totaltime)
        combinedlist.append([currentdate, totaltime])
        currentdate = currentdate + timedelta(days=1)
    with open('subscribedpodcasts.csv', 'w', newline='') as file:
        for p in combinedlist:
            csv.writer(file).writerow(p)
    return datelist, durationlist


validatedinput = False
while not validatedinput:
    generateFile = input('Would you like to generate a new file? (y/N)')
    if generateFile == 'y' or generateFile == 'N':
        validatedinput = True

if generateFile == 'N':
    try:
        with open('podcastlist.csv', 'r') as r:  # read work order data csv file
            csv_reader = csv.reader(r)
            allPodcasts = list(csv_reader)
    except FileNotFoundError:
        print('File not found, creating new file: podcastlist.csv')
else:
    allPodcasts = opmltorss('podcasts_opml.xml')

stringtodatetime(allPodcasts)
allPodcasts.sort(key=lambda x: x[2])  # sort by date, oldest to newest
xlist, ylist = sumduration(allPodcasts)
print('\nThe average new podcasts per day is {} hours, see podcastlist.csv for more information'.format(
    (sum(ylist) / len(ylist))))

# below is a template for using matplotlib to have Python generate a graph - I recommend using Google Sheets instead
'''
plt.plot_date(xlist, ylist, xdate=True)
plt.show()
'''
