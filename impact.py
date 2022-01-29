import sys
import json
from enum import Enum
from datetime import datetime
from collections import defaultdict
from pybliometrics.scopus import ScopusSearch, AuthorSearch

# enumerated type for output quantities
class Output(Enum):
    selfy = 0
    refer = 1
    impct = 2


# compute impact for scientists
def impact(s, pool=set()):

    # data structure used to store results
    results = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # retrieve author
    au = AuthorSearch("AU-ID({})".format(s))
    print("-- Processing results for", au)

    # get articles citing the author
    start = datetime.now().replace(microsecond=0)
    search = ScopusSearch("REFAUID({})".format(s))
    end = datetime.now().replace(microsecond=0)
    print("-- Retrieved citing data from server in {}".format(end - start))

    # analyze list of articles citing the scientist
    # for each article, get the first author and add it to the pool if not done already
    for i, article in enumerate(search.results, 1):  # start enumerate at 1

        # get authorship
        try:
            authorship = [int(j) for j in article.author_ids.split(';')]
        except AttributeError:
            continue

        # get article date
        date = datetime.strptime(article.coverDate, '%Y-%m-%d')

        print(" {}. [{}] {}, {}, {} ({})".format(i, article.aggregationType, article.author_names, article.title,
                                                 article.publicationName, date.year))

        # exclude author if self-citation
        if s in authorship:
            results[s][date.year][Output.selfy] += 1
            print(" - Self-citation found in author list '{}'".format(article.author_names))
            continue

        # get first author
        first = authorship[0]

        # exclude author if in reference list
        if first in pool:
            results[s][date.year][Output.refer] += 1
            print(" - Reference citation found for author")
            continue

        # add first author to reference set
        pool.add(first)

        # count first author towards impact
        results[s][date.year][Output.impct] += 1


    print('\n-- Impact summary for {} {} from a total of {} articles:\n'.format(au.authors[0].surname, au.authors[0].givenname, au.authors[0].documents))
    print(("{:14s}"*5).format('year', 'selfies', 'excl-refs', "impact", "cumulative"))

    # output information year by year
    count = defaultdict(int)
    for k,v in results[s].items():
        try:
            count[Output.selfy] += results[s][k][Output.selfy]
            count[Output.refer] += results[s][k][Output.refer]
            count[Output.impct] += results[s][k][Output.impct]
            print(("{:14s}"*5).format(str(k),
                                  str(results[s][k][Output.selfy]),
                                  str(results[s][k][Output.refer]),
                                  str(results[s][k][Output.impct]),
                                  str(count[Output.impct])))
        except:
            pass

    print("_"*70)
    print(("{:14s}"*5).format("",
                              str(count[Output.selfy]),
                              str(count[Output.refer]),
                              str(count[Output.impct]),
                              str(count[Output.impct])))

    years = len(results[s])
    print("Period: {} years".format(years))
    print("Impact per year: {:.2f}".format(count[Output.impct]/years))
    print("Impact: ", count[Output.impct])

    return count[Output.impct]


if __name__ == "__main__":
    sys.exit(impact(int(sys.argv[1])))
