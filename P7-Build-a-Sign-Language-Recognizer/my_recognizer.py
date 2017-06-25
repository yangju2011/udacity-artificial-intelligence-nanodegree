import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    sequences = test_set.get_all_sequences() 
    Xlengths = test_set.get_all_Xlengths()  
    N = len(test_set.wordlist)
    i = 0
    while i < N: # keep index for guesses
      word = test_set.wordlist[i]
      # X = sequences[i] # each one is a dict
      X,lengths = Xlengths[i]
      prob = dict()
      for key in models:
        train_word = key
        try:
          model = models[key]
          logL = model.score(X,lengths)
          prob[train_word] = logL
        except:
          prob[train_word] = float("-inf")

      probabilities.append(prob)
      max_word = max(prob,key=prob.get)
      guesses.append(max_word)
      i += 1

    return probabilities, guesses
