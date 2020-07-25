from math import sqrt

# Full recommendation system
# USER_BASED COLLABORATIVE FILTERING
# Requirements: Set up a dictionary of people, items and scores and you cna
# use this to create recommendations for any person.

critics = {'Lisa Rose': {'Lady in the Water': 2.5,
                         'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0,
                         'Superman Returns': 3.5,
                         'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0,
                            'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5,
                            'Superman Returns': 5.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5,
                                'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5,
                                'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5,
                            'Just My Luck': 3.0,
                            'The Night Listener': 4.5,
                            'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0,
                            'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0,
                            'Superman Returns': 3.0,
                            'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0,
                             'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0,
                             'Superman Returns': 5.0,
                             'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5,
                    'You, Me and Dupree': 1.0,
                    'Superman Returns': 4.0}
           }


# Euclideon distance
#

# return a distance-based similarity score for person1 and person2

def sim_distance(prefs, person1, person2):
    #     get the list of shared_items

    si = {}

    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    #     if they have no rationgs in common, return 0
    if len(si) == 0: return 0
    # Add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sum_of_squares)


# print(sim_distance(critics, 'Toby', 'Gene Seymour'))


# terminal test functions
# from me2ushop.recommendations import critics
# from math import sqrt
#  reload(recommendations if theres is any changes)
#  recommendatios.sim_distance(recommendations.critics, 'Lisa Rose', 'Gene Seymour')

# Pearson correlation coeffiecient for p1 and p2

def sim_pearson(prefs, p1, p2):
    # get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

        # print(si)
        # find number of similar elements
    n = len(si)

    if n == 0:
        return 0

    #     add up all the preferences ratings that they have in common
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # print('sum 1:', sum1)
    # print('sum 2:', sum2)

    #     Sum up the squares of each rating

    sum1sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2sq = sum([pow(prefs[p2][it], 2) for it in si])

    # print('sumsq 1:', sum1sq)
    # print('sumsq 2:', sum2sq)

    #     sum up all the products

    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
    # print('products sum:', pSum)

    #     calculate Pearson Score

    num = pSum - (sum1 * sum2 / n)
    # print('num', num)
    den = sqrt((sum1sq - pow(sum1, 2) / n) * (sum2sq - pow(sum2, 2) / n))
    if den == 0:
        return 0

    # print('den', den)

    r = num / den

    return r


# This function will return a value between –1 and 1.
# A value of 1 means that the two people have exactly the same ratings for every item


# print(sim_pearson(critics, 'Gene Seymour', 'Toby'))


# http://en.wikipedia.org/wiki/ Metric_%28mathematics%29#Examples
# Other similarity functions to try jaccard coeffiecient or manhattan distance


# RANKING CRITICS
# returns the best matches for person from the prefs dictinary.
# number of results and similarity function are optional params.
# uses python list comprehension
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person
              ]

    #     sort the list so the hightes scores appeat at the top

    scores.sort()
    scores.reverse()
    return scores[0:n]


# print(topMatches(critics, 'Claudia Puig'))


# RECOMMENDING ITEMS

#  To avoid persmissive recommendations, we rank the items that user hasnt seen or bought and
# recommend those items

# gets recommendations for a person by using a weighted average
# of every other user's rankings
# for similarity function you can pass either sim_distance or pearson
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}

    for other in prefs:
        #   don't compare me to myself
        if other == person:
            continue

        sim = similarity(prefs, person, other)

        #        ignore scores of zero or lower
        if sim <= 0:
            continue
        for item in prefs[other]:
            # only score items I havent seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                #                 sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    #     create a nomalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    #     return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings


# print(getRecommendations(critics, 'Gene Seymour'))
# print(getRecommendations(critics, 'Gene Seymour', similarity=sim_distance))


# Matching Products
# Customers who bought this item also bought....
# Determine similarity by looking at who like a particular item, and
# seeing other things they liked.
# Swap the people and the items from the dictionary above!

# function to swap

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            #             flip item and person
            result[item][person] = prefs[person][item]
    return result


movies = transformPrefs(critics)


# Call earlier functions to determine relationship
# The function produces negative values, means those who like the item disliked
# the negative one
# print(topMatches(movies, 'The Night Listener'))

# It’s not always clear that flipping people and items will lead to useful results,
# but in many cases it will allow you to make interesting comparisons

#  Reversing the products with the people, as you’ve done here,
#  would allow us to search for people who might buy certain products
# print(getRecommendations(movies, 'The Night Listener'))


# ITEM BASED COLLABORATIVE FILTERING = Works well with large datasets
# The general technique is to precompute the most similar items for each item.
# Then, when you wish to make recommendations to a user,
# you look at his top-rated items and create a weighted list of the items most similar to those

# Generate a similar item dataset

def calculateSimilarItems(prefs, n=10):
    #     create a dictionary of items showing which other items they
    #  are most similar to

    results = {}

    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        #         status updates for large datasets
        c += 1

        if c % 100 == 0:
            print("%d / %d" % (c, len(itemPrefs)))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_pearson)
        results[item] = scores
    return results


#  as the user base grows, the similarity scores between items
#  will usually become more stable.
itemsim = calculateSimilarItems(critics)


def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    # print(userRatings)
    # print(itemMatch)

    scores = {}
    totalSim = {}

    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # print(item)
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            # print(similarity, item2)

            #  Ignore if the user has already rated/bought the item before
            if item2 in userRatings:
                continue

            # weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # print(scores)

            # sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
            # print(totalSim)

        # Divide each total score by total weighting to get an average
        rankings = [(score / totalSim[item], item) for item, score in scores.items()]
        # return the rankings in desc
        rankings.sort()
        rankings.reverse()
        return rankings


print(getRecommendedItems(critics, itemsim, 'Michael Phillips'))

# Learn more
# “Item-based Collaborative Filtering Recommendation Algorithms” by Sarwar et al.
# at http://citeseer.ist. psu.edu/sarwar01itembased.html.

# 1. Tanimoto score. Find out what a Tanimoto similarity score is.
# In what cases could this be used as the similarity metric instead of Euclidean distance or Pearson coefficient?
# Create a new similarity function using the Tanimoto score.

# 2. Tag similarity. Using the del.icio.us API, create a dataset of tags and items.
# Use this to calculate similarity between tags and see if you can find any that are almost identical.
# Find some items that could have been tagged “programming” but were not

# 3. User-based efficiency. The user-based filtering algorithm is inefficient because it compares a user to all other
# users every time a recommendation is needed. Write a function to precompute user similarities, and alter the
# recommendation code to use only the top five other users to get recommendations

# 4. Item-based bookmark filtering. Download a set of data from del.icio.us and add it to the database.
# Create an item-item table and use this to make item-based recommendations for various users. How do these compare to
# the user-based recommendations?
#
# 5. Audioscrobbler. Take a look at http://www.audioscrobbler.net, a dataset containing music preferences for a
# large set of users. Use their web services API to get a set of data for making and building a
# music recommendation system.
