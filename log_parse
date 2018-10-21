import collections
import datetime
import re
import urllib.parse


def fill_dict(urldict, line, time_dict,
              ignore_files,ignore_urls, request_type,
              ignore_www, slow_queries):

    timer = int(line[6])
    line = urllib.parse.urlparse(line[3])

    if request_type:
        if not request_type == line[2][1:]:
            return

    if slow_queries:
        time_dict[line.netloc + line.path] += timer

    if ignore_urls:
        for url in ignore_urls:
            if url in line[3]:
                return

    if ignore_files:
        if re.search('\.\w{2}', line.path):
            return

    if ignore_www and line.netloc.rfind('www.', 0, 4) == 0:
        urldict[re.sub('www.', '', line.netloc, 1) + line.path] += 1
    else:
        urldict[line.netloc + line.path] += 1

    return urldict


def top5(urldict):
    urllist = sorted(urldict, key = urldict.get, reverse = True)
    urllist = urllist[:5]
    for k in range(len(urllist)):
        urllist[k] = urldict.get(urllist[k])
    return urllist


def bottom5(url_dict, slow_dict):
    bottomlist = sorted(slow_dict, key = slow_dict.get, reverse = True)
    for i in range(len(bottomlist)):
        bottomlist[i] = slow_dict.get(bottomlist[i]) // url_dict.get(bottomlist[i])
    bottomlist.sort(reverse = True)
    bottomlist = bottomlist[:5]
    return bottomlist


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    urldict = collections.defaultdict(int)
    time_dict = collections.defaultdict(int)
    log = open('log.log')

    if start_at:
        start_at = datetime.strptime(start_at, '%d/%b/%Y %X')
    if stop_at:
        stop_at = datetime.strptime(stop_at, '%d/%b/%Y %X')

    for line in log:
        if re.search('\d\d/\w{3}/\d{4}', line):
            line = line.split()
            if start_at or stop_at:
                date = "{} {}".format(line[0][1:], line[1][:-1])
                date = datetime.strptime(date, '%d/%b/%Y %X')
                if (not start_at or start_at < date) and (not stop_at or stop_at > date):
                    fill_dict(urldict, line, time_dict,
                              ignore_files, ignore_urls, request_type,
                              ignore_www, slow_queries)
            else:
                fill_dict(urldict, line, time_dict,
                          ignore_files, ignore_urls, request_type,
                          ignore_www, slow_queries)
    if slow_queries:
        return bottom5(urldict, time_dict)
    else:
        return top5(urldict)


print(parse())
