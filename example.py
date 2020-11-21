import chains
import json
from pprint import pprint
import statistics
import neuralcoref
import spacy, json
import math

nlp = spacy.load("en_core_web_lg")
neuralcoref.add_to_pipe(nlp)

def parse_test_instance(story):
    """Returns TWO ParsedStory instances representing option 1 and 2"""
    # this is very compressed
    id = story.InputStoryid
    story = list(story)
    sentences = [chains.nlp(sentence) for sentence in story[2:6]]
    alternatives = ["", ""]
    return [chains.ParsedStory(id, id, chains.nlp(" ".join(story[2:6]+[a])), *(sentences+[chains.nlp(a)])) for a in alternatives]

def parse_test_instance2(story):
    """Returns TWO ParsedStory instances representing option 1 and 2"""
    # this is very compressed
    id = story.InputStoryid
    story = list(story)
    sentences = [chains.nlp(sentence) for sentence in story[2:6]]
    alternatives = [story[6], story[7]]
    return [chains.ParsedStory(id, id, chains.nlp(" ".join(story[2:6]+[a])), *(sentences+[chains.nlp(a)])) for a in alternatives]

def to_story(story, id):
    return [chains.ParsedStory(id, id, chains.nlp(story)), *[]]

def story_answer(story):
    """Tells you the correct answer. Return (storyid, index). 1 for the first ending, 2 for the second ending"""
    #obviously you can't use this information until you've chosen your answer!
    return story.InputStoryid, story.AnswerRightEnding


# Load training data and build the model
# data, table = chains.process_corpus("train.csv")
# print(table.pmi("move", "nsubj", "move", "nsubj"))

count = 0
# load the pre-built model
with open("all.json") as fp:
    table = chains.ProbabilityTable(json.load(fp))

def extract_dependency_five(parse):
    """Get a story, return a list of dependency pairs"""
    verbs = [verb for verb in parse if verb.pos_ == "VERB"]
    list = []
    for verb in verbs:
        for child in verb.children:
            # Add the word/dependency pair to the identified entity
            tup = (verb.lemma_, child.dep_)
            list.append(tup)
    return list


# # load testing data

test = chains.load_data("val.csv")
result = [0, 0]
for t in test:
    one, two = parse_test_instance2(t) #does have ending
    three, four = parse_test_instance(t) #doesnt have ending
    one_deps = chains.extract_dependency_pairs(three)
    two_deps = chains.extract_dependency_pairs(four)
    one_deps1 = chains.extract_dependency_pairs(one)
    two_deps1 = chains.extract_dependency_pairs(two)
    one_pmi = []
    two_pmi = []
    decision_verb = extract_dependency_five(one.five)
    decision_verb2 = extract_dependency_five(two.five)

    correct_ans = '0'

    if(len(decision_verb) == 0 | len(decision_verb2) == 0): continue

    for choice in decision_verb:
        if(choice in one_deps1[1][0]) & (len(one_deps[1][0]) != 0):
            one_pmi.append(table.pmi(choice[0], choice[1], one_deps[1][0][-1][0], one_deps[1][0][-1][1]))

    for choice in decision_verb2:
        if(choice in two_deps1[1][0]) & e(len(two_deps[1][0]) != 0):
            two_pmi.append(table.pmi(choice[0], choice[1], two_deps[1][0][-1][0], two_deps[1][0][-1][1]))

    try:
        result_1 = statistics.mean(one_pmi)
        result_2 = statistics.mean(two_pmi)
        if statistics.mean(one_pmi) > statistics.mean(two_pmi):
            correct_ans = '2'
        else:
            correct_ans = '1'

        if (correct_ans == str(story_answer(t)[1])):
            result[1] += 1
        # else:
            # pprint(three[2:])
            # pprint(four[2:])
            # pprint([one_pmi, two_pmi])
            # # logic to choose between one and two
            # pprint("answer:" + str(story_answer(t)))
        result[0] += 1
    except ValueError:
        print('the verb pair is not inside the dicts')

    count += 1
    pprint([count, result])
print(result)
