"""Python rewrite of Mark Rosenfelder’s Sound Change Applier as a module.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

SCA² (C) 2012 Mark Rosenfelder aka Zompist (markrose@zompist.com)
Python re-code (C) 2015 Andreas Kübrich aka Schyrsivochter (andreas.kuebrich@kuebrich.de)"""


import re, sys

gdebug = False

class SCAError(Exception):
    "Error class for everything SCA-related (e.g. invalid rules or categories)"
    pass

def printDebug(funcName, *args):
    if gdebug:
        print(f"\nDebug info from {funcName}:", file=sys.stderr)
        for name, value in args:
            print(f"{name} = {value!r}", file=sys.stderr)

def ruleExToRegex(expression, categories, numGroups):
    """Transform a part of a sound change rule into a regular expression.

Arguments:
    expression : string
    categories : dict {"A": "abc", ...}
    numGroups  : integer
Returns a tuple (regExpression, numGroups).

numGroups is used internally to count the number of capture groups, which
are used for degemination."""

    regExpression = ""
    brackets = False
    lastWasBracket = False
    for char in expression:
        oldchar = char
        if   char == "#":
            char = " "
        elif char == "[":
            brackets = True
            lastWasBracket = True
            char = "("
            numGroups += 1
        elif char == "]":
            brackets = False
            regExpression = regExpression[:-1] # delete the last |
            char = ")"
        elif char == "(":
            numGroups += 1
        elif char == ")":
            char = ")?"
        elif char in categories:
            numGroups += 1
            catContent = categories[char]
            char = "([" + catContent + "])"
        elif char == "\u00b2":
            if len(regExpression) and not regExpression[-1] == ")":
                regExpression = regExpression[:-1] + "(" + regExpression[-1] + ")"
                numGroups += 1
            char = f"\\{numGroups}"
        elif char in ".\\?|+*^${}":
            char = f"\\{char}"
        else:
            pass
        regExpression += (char + "|") if (brackets and not lastWasBracket) else char
        lastWasBracket = False
        printDebug("ruleExToRegex", ("regExpression", regExpression), ("oldchar", oldchar), ("char", char), ("numGroups", numGroups))
    return regExpression, numGroups

def ruleToRegex(target, environment, categories):
    """Transform a sound change rule into a set of regular expressions.

Arguments:
    target      : string
    environment : tuple (envBefore, envAfter)
    categories  : dict {"A": "abc", ...}
Returns a tuple (wholeRE, beforeRE, targetRE, afterRE)."""

    envsplit = environment.split("_")
    if len(envsplit) != 2:
        raise SCAError(f'Bad sound change rule environment: "{environment}" (must contain exactly one underscore)')
    envBefore, envAfter = envsplit
    befRE, numGroups = ruleExToRegex(envBefore, categories, 0)
    numGroups += 1
    tgtIndex = numGroups
    tgtRE, numGroups = ruleExToRegex(target, categories, numGroups)
    tgtRE = f"({tgtRE})"
    aftRE, numGroups = ruleExToRegex(envAfter, categories, numGroups)
    printDebug("ruleToRegex",("target", target), ("environment", environment), ("envBefore", envBefore), ("envAfter", envAfter), ("result", (befRE + tgtRE + aftRE, befRE, tgtRE, aftRE)))
    return befRE + tgtRE + aftRE, befRE, tgtRE, aftRE, tgtIndex

def replace(tgtword, rule, categories):
    target, replacement, envDummy, excDummy = rule
    if replacement == "\\\\": # metathesis
        return tgtword[::-1]
    if not target: # epenthesis
        return replacement
    doCatRep = target[0] in categories
    if doCatRep: # if category replacement is needed
        tgtKey = target[0]
        tgtCat = categories[tgtKey]
        tgtIdx = tgtCat.find(tgtword[0]) # index in the category
    replacestr = ""
    for char in replacement:
        if doCatRep and (char in categories):
            repCat = categories[char]
            char = "" if len(repCat) <= tgtIdx else repCat[tgtIdx]
        if char == "\u00b2": # gemination
            char = replacestr[-1] # last character
        replacestr += char
    return replacestr

def applyRule(word, rule, categories):
    """Apply a single rule to a word.

Arguments:
    categories : dict {"A": "abc", ...}
    rule       : tuple (target, replacement, environment, exception)
    word       : string
Returns the output word.

Exception may be an empty string."""

    target, replacement, environment, exception = rule
    try:
        envmtRE, envBefRE, tgtRE, envAftRE, tgtIndex = ruleToRegex(target, environment, categories)
    except SCAError as e:
        raise SCAError('Bad sound change rule: "' + "/".join(rule if exception else rule[0:3]) + '" (environment must contain exactly one underscore)') from e
    if exception:
        try:
            excptRE, excBefRE, dummy, excAftRE, etgtIndex = ruleToRegex(target, exception, categories)
        except SCAError as e:
            raise SCAError('Bad sound change rule: "' + "/".join(rule) + '" (exception must contain exactly one underscore)') from e
    else:
        excptRE = None

    # tgtpos is the position of the target, pos is the one of the environment
    tgtpos = 1
    pos = 0
    isEpen = not (tgtRE or envBefRE) # if rule is epenthesis before something
    while pos < len(word):
        oldWord = word
        envMatch = re.match(envmtRE, word[pos:])
        if envMatch:
            # find out about the environment
            envMatchEnd = envMatch.end()
            envMatchedWord = envMatch.string[:envMatchEnd]

            # then about the target
            tgtStart, tgtEnd = envMatch.regs[tgtIndex]
            tgtWord = envMatchedWord[tgtStart:tgtEnd] # the substring to replace
            if pos + tgtStart != tgtpos: # if we are not arrived yet
                printDebug("applyRule", ("pos", pos), ("tgtpos", tgtpos), ("tgtStart", tgtStart))
                if tgtpos == pos:
                    tgtpos += 1
                    pos = 0
                else:
                    pos += 1
                continue
            excApplies = False
            etgtStart = None
            etgtEnd = None
            excMatchedWord = None
            # find out about the exception, if there is one
            if exception:
                for expos in range(len(word)):
                    excMatch = re.match(excptRE, word[expos:])
                    if excMatch:
                        excMatchEnd = excMatch.end()
                        excMatchedWord = excMatch.string[:excMatchEnd]
                        # then about the exception target
                        etgtStart, etgtEnd = excMatch.regs[etgtIndex]
                        if expos + etgtStart == tgtpos: # if they both match the same thing
                            excApplies = True
                            break
            
            repword = tgtWord if excApplies else replace(tgtWord, rule, categories)
            
            word = word[:pos] + envMatchedWord[:tgtStart] + repword + envMatchedWord[tgtEnd:] + word[pos+envMatchEnd:]
            printDebug("applyRule", ("pos", pos), ("rule", rule), ("envMatchedWord", envMatchedWord), ("excMatchedWord", excMatchedWord), ("tgtStart", tgtStart), ("tgtEnd", tgtEnd),
                       ("etgtStart", etgtStart), ("etgtEnd", etgtEnd), ("tgtWord", tgtWord), ("repword", repword), ("excApplies", excApplies), ("word", word), ("oldWord", oldWord))
            # move behind that which already has been processed
            tgtpos += len(repword) + (1 if isEpen else 0) # add 1 on epenthesis before something – else we’ll get caught in an endless loop
        if tgtpos == pos:
            tgtpos += 1
            pos = 0
        else:
            pos += 1
        printDebug("applyRule", ("pos", pos), ("tgtpos", tgtpos))
    return word
            

def transformWord(word, rules, categories):
    """Transform a word according to the categories and rules.

Arguments:
    categories : dict {"A": "abc", ...}
    rules      : list of tuples (target, replacement, environment, exception)
    word       : tuple (word, gloss)
Returns a tuple (inword, outword, gloss).

Exception and gloss may be empty strings."""

    inw, gloss = word
    word = inw
    for rule in rules:
        word = applyRule(word, rule, categories)
        printDebug("transformWord", ("inw", inw), ("word", word))

    return inw, word, gloss
    

def transformWords(words, rules, categories):
    """Transform a set of words according to the categories and rules.

Arguments:
    categories : dict {"A": "abc", ...}
    rules      : list of tuples (target, replacement, environment, exception)
    words      : list of tuples (word, gloss)
Returns a list of tuples (inword, outword, gloss).

Exception and gloss may be empty strings."""

    return [transformWord(word, rules, categories) for word in words]

def rewrite(word, rules):
    """Apply the rewrite rules to the word.

Arguments:
    word  : string
    rules : list of tuples (original, rewrite)
Returns a string."""

    for rule in rules:
        word = word.replace(rule[0], rule[1])
    return word

def unrewrite(word, rules):
    """Apply the rewrite rules reversed.

Arguments:
    word  : string
    rules : list of tuples (original, rewrite)
Returns a string."""

    for rule in rules:
        word = word.replace(rule[1], rule[0])
    return word

def sca(categories, rules, words, outFormat=0, rewrites=[], rewOut=False, debug=False):
    """Apply the specified sound changes to the words. Basically Mark Rosenfelder's SCA\u00b2.

Arguments:
    categories : list of category strings
    rules      : list of rule strings
    words      : list of word strings, including glosses
    outFormat  : format of the output, either:
        - a format string, with
            {inw}: the original word
            {outw}: the transformed word
            {gloss}: the gloss, including the gloss symbol \u2023
        - a number from 0 to 2 specify a preset output format from the SCA²:
            0: "{outw}{gloss}"
            1: "{inw} \u2192 {outw}{gloss}"
            2: "{outw}{gloss} [{inw}]"
        Defaults to 0.
    rewrites   : List of rewrite rules. Defaults to ""
    rewOut     : Whether the rewrite rules should be reverted on the
        output. Defaults to False.
    debug      : Whether to print debug information to stderr. WARNING:
        VERY extensive. Use with care and with as few words and rules as
        possible. Defaults to False.
Returns a list of output strings according to the output format."""

    global gdebug
    gdebug = debug

    # check and convert rewrites into a list
    rews = []
    for rule in rewrites:
        if rule.strip() == "":
            continue
        if rule.count("|") != 1:
            raise SCAError(f'Invalid rewrite rule: "{rule}" (must contain exactly one pipe)')
        rews.append(rule.split("|"))
    
    def   rew(word, addSpace): return (" " + rewrite(word, rews).strip() + " ") if addSpace else rewrite(word, rews).strip()
    def unrew(word, ignoreRO): return      unrewrite(word, rews).strip() if (ignoreRO or rewOut) else word.strip()
    
    # rewrite, check and convert categories into a dict
    cats = {}
    for cat in categories:
        cat = rew(cat, False)
        if cat == "":
            continue
        try:
            catKey, catContent = cat.split("=")
        except ValueError as e:
            raise SCAError(f'Bad category: "{cat}" (must contain excactly one equals sign)')
        if len(catKey) != 1:
            raise SCAError(f'Bad category: "{cat}" (category identifier must be exactly one character')
        cats[catKey] = catContent # "A=abc" -> "A":"abc"
    
    # rewrite, check and convert rules
    exRules = []
    for rule in rules:
        rule = rew(rule, False)
        if rule == "" or rule[0] == "*": # empty or comment
            continue
        rule = rule.replace("\u2192", "/")
        # append a / to all rules that don’t have an exception
        if rule.count("/") == 2:
            rule += "/"
        elif rule.count("/") != 3:
            raise SCAError(f'Bad sound change rule: "{rule}" (must contain two or three slashes)')
        exRules.append(rule)
    # convert rules into a list of tuples
    rules = [tuple(rule.split("/")) for rule in exRules] # "A/b/_c/d_" -> ["A","b","_c","d_"]
    
    # rewrite and convert words
    gwords = []
    for word in words:
        part = list(word.partition("\u2023"))
        if part[1]: part[1] = " " + part[1]
        gwords.append((part[0], part[1] + part[2]))
    # convert words into a list of tuples
    words = [(rew(word[0], True), word[1]) for word in gwords] # "acy \u2023 asu" -> ["acy"," \u2023 asu"]

    # transform the words according to the sound change rules
    transformed = transformWords(words, rules, cats)
    printDebug("sca",("words", words), ("rules", rules), ("categories", cats), ("rews", rews), ("transformed[0]", transformed[0] if transformed else None))

    # replace outFormat indices with format strings
    if type(outFormat) is int:
        outFormat = [
            "{outw}{gloss}",
            "{inw} \u2192 {outw}{gloss}",
            "{outw}{gloss} [{inw}]"
            ][outFormat]
        
    return [(outFormat.format(outw=unrew(outw, False), inw=unrew(inw, True), gloss=gloss) if any([unrew(inw, True), unrew(outw, True), gloss]) else "") for inw, outw, gloss in transformed]


def printsca(categories, rules, words, outFormat=0, rewrites=[], rewOut=False, debug=False, file=sys.stdout):
    """Apply the specified sound changes to the words. Basically Mark Rosenfelder's SCA\u00b2.

Arguments:
    categories : list of category strings
    rules      : list of rule strings
    words      : list of word strings, including glosses
    outFormat  : format of the output, either:
        - a format string, with
            {inw}: the original word
            {outw}: the transformed word
            {gloss}: the gloss, including the gloss symbol \u2023
        - a number from 0 to 2 specify a preset output format from the SCA²:
            0: "{outw}{gloss}"
            1: "{inw} \u2192 {outw}{gloss}"
            2: "{outw}{gloss} [{inw}]"
        Defaults to 0.
    rewrites   : List of rewrite rules. Defaults to []
    rewOut     : Whether the rewrite rules should be reverted on the
        output. Defaults to False.
    debug      : Whether to print debug information to stderr. WARNING:
        VERY extensive. Use with care and with as few words and rules as
        possible. Defaults to False.
Prints the output according to the output format."""
    
    print(*sca(categories, rules, words, outFormat, rewrites, rewOut, debug), sep="\n", file=file)


class SCAConf:
    """Class for an SCA configuration. Holds all input fields.

Attributes:
    categories : list of category strings
    rules      : list of rule strings
    inLex      : list of word strings, including glosses
    outFormat  : format of the output, either:
        - a format string, with
            {inw}: the original word
            {outw}: the transformed word
            {gloss}: the gloss, including the gloss symbol \u2023
        - a number from 0 to 2 specify a preset output format from the SCA²:
            0: "{outw}{gloss}"
            1: "{inw} \u2192 {outw}{gloss}"
            2: "{outw}{gloss} [{inw}]"
        Defaults to 0.
    rewrites   : List of rewrite rule strings. Defaults to []
    rewOut     : Whether the rewrite rules should be reverted on the
        output. Defaults to False.
    debug      : Whether to print debug information to stderr. WARNING:
        VERY extensive. Use with care and with as few words and rules as
        possible. Defaults to False.
"""

    def __init__(self, categories=[], rules=[], inLex=[], outFormat=0, rewrites=[], rewOut=0, debug=0):
        self.categories = categories
        self.rules = rules
        self.inLex = inLex
        self.outFormat = outFormat
        self.rewrites = rewrites
        self.rewOut = rewOut
        self.debug = debug
        
    def sca(self):
        "Run the SCA and return the output as a list."
        return sca(self.categories, self.rules, self.inLex, self.outFormat, self.rewrites, self.rewOut, self.debug)
    
    def printsca(self, file=sys.stdout):
        "Run the SCA and print the outputs."
        printsca(self.categories, self.rules, self.inLex, self.outFormat, self.rewrites, self.rewOut, self.debug, file=file)

example = SCAConf(
    categories = [
        "V=aeiou",
        "L=āēīōū",
        "C=ptcqbdgmnlrhs",
        "F=ie",
        "B=ou",
        "S=ptc",
        "Z=bdg"
    ],
    rules = [
        "[sm]//_#",
        "i/j/_V",
        "L/V/_",
        "e//Vr_#",
        "v//V_V",
        "u/o/_#",
        "gn/nh/_",
        "S/Z/V_V",
        "c/i/F_t",
        "c/u/B_t",
        "p//V_t",
        "ii/i/_",
        "e//C_rV"
    ],
    inLex = [
        "lector",
        "doctor",
        "focus",
        "jocus",
        "districtus",
        "cīvitatem",
        "adoptare",
        "opera",
        "secundus",
        "fīliam",
        "pōntem",
    ],
    rewrites = ["lh|lj"],
    rewOut = 1
)

if __name__ == "__main__":
    example.printsca()
