from get_features import update_feat_vect
from nlp import stanford_nlp

if __name__ == '__main__':
    pos, tree, dep = stanford_nlp.get_parses('I am unsure if i like dogs. I do not hate cats. Ahh. Now I see why you turned into an agnostic, if you even believed Christianity in the first place.')
    for index in range(len(pos)):
        l, r = update_feat_vect(dep[index], pos[index])
        for element in r:
            word, dominates = element
            for token in dominates:
                print word, token

