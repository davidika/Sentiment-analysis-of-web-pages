"""
A program to process WARC files and extract information from the HTML data within.
The program analyses text to address the following insights.
    1. How 'positive' is Australia?
    2. How positive does Australia feel toward their Government?
    3. How patriotic is Australia compared with the UK and Canada?
    4. What are the most referred-to domains by Australian websites?

Author: David Ika
Date: 10 Oct 2020
"""

# General helper functions
    
    ## remove punctuation:

def remove_punc(word):
    punc = '''`~!@#$%^&*()_=[]\{}|;':",./<>?+-''' # 32 non-alphanumeric characters
    for nonalpha in punc:
        if nonalpha in word:
            word = word.replace(nonalpha, "")
    return word

    ## split & extract base url:

def get_base_url(url):
    url = url.lower()
    if url.startswith('https://') or url.startswith('http://'):
        url = url.replace('https://', '')
        url = url.replace('http://', '')
    url = url.split('/')[0]
    url = url.split(':')[0]
    url = url.split('?')[0]
    url = url.split('#')[0]
    url = url.split('>')[0]
    url = url.split('%')[0]
    return url.split(' ')[0]

    ## split & extract sentences:

def get_sentences(html):
    first_sentences = html.lower().split('.')

    second_sentences = []
    for sentence in first_sentences:
        second_sentences.extend(sentence.split('?'))
    del(first_sentences)

    final_sentences = []
    for sentence in second_sentences:
        final_sentences.extend(sentence.split('!'))
    del(second_sentences)

    return final_sentences

    ## parse HTML:

def process_html(html):
    html = html.lower()
    html = html.replace('\n', ' ')
    html = html.replace('\r', ' ')
    html = html.replace('\t', ' ')
    index = 0
    while True:
            # check for javascript tags:
        if html.find('<script', index) != -1 and html.find('</script', index) != -1:
                # within those tags:
            start_index = html.find('<script', index)
            end_index = html.find('>', start_index)
            end_index = html.find('</script', end_index)
            end_index = html.find('>', end_index)
                # add to HTML list:
            html = html[:start_index] + html[end_index:]
            index = start_index + 1
            continue
        break
    index = 0
    while True:
        # check for html tags:
        if html.find('<',index) != -1 and html.find('>',index) != -1:
                # within those tags:
            start_index = html.find('<', index)
            end_index = html.find('>', start_index)
                # add to HTML list:
            html = html[:start_index + 1] + html[end_index:] # review space
            index = start_index + 1
            continue
        break
    return (html)

    ## read files and form set:

def read_words(file):
    with open(file) as f:
        words = f.read()
        words = words.split()
    return set(words)


# Insight-specific functions:
    
    ## insight 1:

def insight_1(html, positive_words, negative_words):
    words = remove_punc(html).lower().split()
    p = [word for word in words if word in positive_words]
    n = [word for word in words if word in negative_words]
    return len(p), len(n)

def agg_insight_1(items):
    positive = 0
    negative = 0
    for p,n in items:
        positive += p
        negative += n
    if negative:
            # solve for ZeroDivisionError
        ratio = round(positive / negative, 4) if negative != 0 else None
    else:
        ratio = None
        # insight 1 average calc & solve for ZeroDivisionError
    average_positive = round(positive / len(items), 4) if len(items) != 0 else None
    average_negative = round(negative / len(items), 4) if len(items) != 0 else None
    return [positive, negative, ratio, average_positive, average_negative]

    ## insight 2:

def insight_2(html, positive_words, negative_words):
    result = []
    final_sentences = get_sentences(html)

    for sentence in final_sentences:
        sentence = sentence.lower()
        sentence = remove_punc(sentence)
        if 'government' in sentence.split():
            p,n = insight_1(sentence, positive_words, negative_words)
            result.append([p,n])
    return result

def agg_insight_2(insight_2_dict):
    positive = 0
    negative = 0
    for li in insight_2_dict.values():
        for p,n in li:
                # rules for determining status of sentence:
            if p != 0 and n == 0:
                positive += 1
            elif p == 0 and n == 1:
                negative += 1
            elif p == 0 and n == 2:
                positive += 1
            elif p == 0 and n > 2:
                negative += 1
    if negative:
        ratio = round(positive / negative, 4) if negative != 0 else None
    else:
        ratio = None
        # insight 2 average calc & solve for ZeroDivisionError
    average_positive = round(positive/len(insight_2_dict), 4) if len(insight_2_dict) != 0 else None
    average_negative = round(negative/len(insight_2_dict), 4) if len(insight_2_dict) != 0 else None
    return [positive, negative, ratio, average_positive, average_negative]

    ## insight 3:

def insight_3(html, phrases, uri):
    html = remove_punc(html).lower()
    count = 0
    for phrase in phrases:
        if len(phrase.split(' ')) > 1:
            count += html.count(phrase)
            html = html.replace(phrase, "")
        else:
            words = html.split()
            count += words.count(phrase)
            html = ' '.join(words).replace(phrase, "")

    words = html.split()
    words = [remove_punc(word.lower())
             for word in words
             if remove_punc(word)]
    return count, len(words) + count

def agg_insight_3(insight_3_dict):
    result = []
    for ci in ['au', 'ca', 'uk']:
        total_phrase = 0
        total_words = 0
        for phrase, words in insight_3_dict[ci].values():
            total_phrase += phrase
            total_words += words
        print(ci,total_phrase,total_words) # # printcheck for country phrases & word counts.
        if total_words:
            ratio = round(total_phrase * 100 / total_words, 4)
        else:
            ratio = None
        result.append(ratio)
    return result

    ## insight 4:

def insight_4(html):
    html = html.lower()
    html = html.split('<a')
        # create list of links:
    all_links = []
    for link in html:
        all_links.append(link.split('>')[0])
    html = all_links
    all_links = []
    for link in html:
            # link determination:
        if "href=" in link:
            link = link.split('href=')[1]
            all_links.append(link)
    links = {}
    for link in all_links:
        link = link.replace('"', '')
        link = link.replace("'", '')
        link = get_base_url(link)
            # do not consider url-length below 3:
        if len(link)<3:
            continue
        if link in links:
            links[link] += 1
        else:
            links[link] = 1
    return links

    # general insight processing:
def process_content(content, uri, insight_1_dict, insight_2_dict, insight_3_dict,
                     insight_4_dict, positive, negative):
    html = process_html(' '.join(content))
    base_url = get_base_url(uri)
        # check for australian domain:
    if base_url.endswith('.au'):
        insight_1_dict[uri] = insight_1(html, positive, negative)
        insight_2_dict[uri] = insight_2(html, positive, negative)
        insight_3_dict['au'][uri] = insight_3(html, ['australia'], uri)
        i4 = insight_4(' '.join(content))
        for u,c in i4.items():
            if u in insight_4_dict:
                insight_4_dict[u] += c
            else:
                insight_4_dict[u] = c
        # check for other countries' domains:
    elif base_url.endswith('.ca'):
        insight_3_dict['ca'][uri] = insight_3(html, ['canada'],uri)
    elif base_url.endswith('.uk'):
        insight_3_dict['uk'][uri] = insight_3(html,
                                              ['united kingdom',
                                               'great britain',
                                               'uk'], uri)

def main (WARC_fname, positive_words_fname, negative_words_fname):
        # list for all HTML data to be processed:
    content = []
        # dictionaries of URIs for each insight:
    insight_1_dict = {}
    insight_2_dict = {}
    insight_3_dict = {'au':{},'ca':{},'uk':{}}
    insight_4_dict = {}
    with open(WARC_fname,'rb') as f:
            #count html content:
        html_counter = 0
            # read in positive and negative words:
        positive = read_words(positive_words_fname)
        negative = read_words(negative_words_fname)
        for i, line in enumerate(f):
            line = line.decode('ascii', 'ignore')
                # process for lines with WARC/1.0:
            if line.strip() == "WARC/1.0":
                # only process once content added (based on lines 277 onward):
                if content:
                        # process content:
                    process_content(content, uri, insight_1_dict, insight_2_dict,
                                     insight_3_dict, insight_4_dict, positive, negative)
                    html_counter = 0
                        # once processed, clear list (for efficiency):
                    content = []
                # extract URIs:
            elif line.lower().strip().startswith('warc-target-uri:'):
                uri = line.lower().replace('warc-target-uri:', '').strip()
            elif line.strip().lower().startswith('content-type:'):
                if 'text/html' in line.lower():
                    content.append(' ')
            elif (line.strip().lower().startswith('<')):
                content.append(line)
                html_counter = 1
                # append when HTML count = 1:
            elif html_counter:
                content.append(line)
        if content:
            process_content(content, uri, insight_1_dict, insight_2_dict,
                             insight_3_dict, insight_4_dict, positive, negative)
        # form list of results and append results of each insight:
    result = []
    result.append(agg_insight_1(insight_1_dict.values()))
    result.append(agg_insight_2(insight_2_dict))
    result.append(agg_insight_3(insight_3_dict))
        # return i4 considering sorting requirements:
    i4 = sorted(insight_4_dict.items(), key = lambda x:x[0])
    i4 = sorted(i4, key = lambda x:x[1], reverse = True)[:5]
    result.append(i4)
    return result

print(main("warc_sample_file.warc", "positive_words.txt", "negative_words.txt"))
