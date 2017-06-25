import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        pass
        #raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except ValueError:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        min_bic = float("inf") # largest logL
        N, n_features = self.X.shape
        num_hidden_states = self.min_n_components
        best_num_components = num_hidden_states
        while num_hidden_states <= self.max_n_components:
            try:
            	# num_params = num_hidden_states * (num_hidden_states - 1) + 2 * num_hidden_states * num_features
                model = GaussianHMM(n_components=num_hidden_states, n_iter=1000).fit(self.X, self.lengths)  # for this word only
                logL = model.score(self.X, self.lengths)   
                n_params = num_hidden_states ** 2 + 2 * n_features * num_hidden_states  - 1
                bic = -2 * logL + n_params * math.log(N) 
                if bic < min_bic:
                    min_bic = bic
                    best_num_components = num_hidden_states
            except ValueError:
                pass
            num_hidden_states += 1

        return self.base_model(best_num_components)

        # TODO implement model selection based on BIC scores
        # raise NotImplementedError


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection based on DIC scores
        # logL - all other log L
        num_hidden_states = self.min_n_components
        max_dic = float("-inf") # largest logL
        best_num_components = num_hidden_states

        other_words = dict()
        for word in self.words:
            if word != self.this_word:
                seq = self.words[word]
                X,lengths = self.hwords[word]
                other_words[word] = (X,lengths)

        while num_hidden_states <= self.max_n_components:
            try:
                model = GaussianHMM(n_components=num_hidden_states, n_iter=1000).fit(self.X, self.lengths)  
                logL = model.score(self.X, self.lengths)

                other_logLs = []   
                for word in other_words:
                    X, lengths = other_words[word]
                    try:
                        model_i = GaussianHMM(n_components=num_hidden_states, n_iter=1000).fit(X, lengths)
                        logL_i = model_i.score(X, lengths)
                        other_logLs.append(logL_i)
                    except ValueError:
                        pass
                
                if len(other_logLs) > 0:
                    other_logL = np.mean(other_logLs)
                    dic = logL - other_logL
                else:
                    other_logL = 0

                if dic > max_dic:
                    max_dic = dic
                    best_num_components = num_hidden_states

            except ValueError:
                pass
                
            num_hidden_states += 1

        return self.base_model(best_num_components)
        raise NotImplementedError


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # TODO implement model selection using CV
        num_hidden_states = self.min_n_components
        max_logL = float("-inf") # largest logL
        best_num_components = 0
        while num_hidden_states <= self.max_n_components:
            if len(self.sequences) < 3:
                split_method = KFold(n_splits = 2)
            else:
                split_method = KFold()
            logLs = []
            # use sequences from this single word only
            for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                X_train, lengths_train = combine_sequences(cv_train_idx,self.sequences)
                X_test, lengths_test = combine_sequences(cv_test_idx,self.sequences)
                try: 
                    model = GaussianHMM(n_components=num_hidden_states, n_iter=1000).fit(X_train, lengths_train)               
                    logL = model.score(X_test, lengths_test)
                    logLs.append(logL)
                except ValueError:
                    # eliminate non-viable data 
                    pass 
            cv_logL  = np.mean(logLs)
            if cv_logL > max_logL:
                max_logL  = cv_logL
                best_num_components = num_hidden_states 
            num_hidden_states += 1
        return self.base_model(best_num_components)
        # raise NotImplementedError
