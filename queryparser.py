#!/usr/bin/env python

import pyparsing
from pyparsing import Keyword, QuotedString, Suppress, Group, Word, Optional, \
     Forward, CaselessLiteral, oneOf, Combine, nums, delimitedList, ZeroOrMore, \
     operatorPrecedence, opAssoc

from table import ColumnQuery, JunctionQuery, NotQuery, MultiJunctionQuery

import unittest

K_OR  = Keyword("or", caseless=True)
K_AND = Keyword("and", caseless=True)
K_IS  = Keyword('is')
K_NOT = Keyword('not')
K_IN  = Keyword('in', caseless=True)
L_PAREN = Suppress('(')
R_PAREN = Suppress(')')

K_WHERE = Keyword('where', caseless=True)

K_EQ = Keyword('=')
K_LTE = Keyword('<=')
K_GTE = Keyword('>=')

quotedString = QuotedString("'")

columnName = Word(pyparsing.alphas)

def parse_condition(toks):
    (col, op, val) = toks
    if op == '=':
        op = ColumnQuery.TYPE_EQ
    elif op == '>=':
        op = ColumnQuery.TYPE_GTE
    elif op == '<=':
        op = ColumnQuery.TYPE_LTE
    else:
        raise Exception("Bad op: " + op)

    return ColumnQuery(col, val, op)

def parse_in_condition(toks):
    (colname, in_text, options) = toks

    queries = [ColumnQuery(colname, opt) for opt in options]
    return MultiJunctionQuery(queries, JunctionQuery.OP_OR)

def parse_junction(toks):
    toks = toks[0]
    queries = [toks[0]]

    op = None
    for i in xrange(1, len(toks), 2):
        this_op = toks[i]
        if op != None and this_op != op:
            raise Exception("mixed ops in toks: " + toks)
        op = this_op
        queries.append(toks[i+1])

    op = op.upper()
    if op == 'AND':
        op = JunctionQuery.OP_AND
    elif op == 'OR':
        op = JunctionQuery.OP_OR
    else:
        raise Exception("bad logical op: " + op)
    
    return MultiJunctionQuery(queries, op)

def parse_not(toks):
    return NotQuery(toks[0][1])


whereExpression = Forward()

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) +
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) +
            Optional( E + Optional("+") + Word(nums) ) )
intNum.setParseAction(lambda t: int(t[0]))

columnRval = realNum | intNum | quotedString

binCondition = ( columnName + binop + columnRval ).setParseAction(parse_condition);

inCondition =  ( columnName + K_IN + L_PAREN + Group(delimitedList( columnRval )) + R_PAREN )
inCondition.setParseAction(parse_in_condition)

whereCondition = (
    binCondition |
    inCondition |
#    ( columnName + in_ + "(" + selectStmt + ")" ) |
    ( "(" + whereExpression + ")" )
    )

whereExpression = operatorPrecedence(
    whereCondition,
    [
    ("not", 1, opAssoc.RIGHT, parse_not),
    ("and", 2, opAssoc.LEFT, parse_junction),
    ("or", 2, opAssoc.LEFT, parse_junction),
    ])

whereExpressionIncWhere = Suppress(K_WHERE) + whereExpression

class Parser:
    def parse(self, string):
        return whereExpressionIncWhere.parseString(
            string,
            parseAll=True)[0]

class ParserTestCase(unittest.TestCase):
    def ptest(self, form, string):
        res = form.parseString(string, parseAll=True)
        if len(res) != 1:
            raise Exception("bad res: " + repr(res))
        return str(res[0])

    def testCondition(self):
        self.assertEqual(self.ptest(whereExpression, "a = 'hello'"),
                         '(a = hello)')

        self.assertEqual(
            self.ptest(whereExpression,
                       "a = 'hello' and b = 'helloworld'"),
            '((a = hello) AND (b = helloworld))')

        self.assertEqual(
            self.ptest(whereExpression,
                       "a = 'hello' or b = 'helloworld'"),
            '((a = hello) OR (b = helloworld))')

        self.assertEqual(
            self.ptest(whereExpression,
                       "a = 'hello' or b = 'helloworld' and c = 'hi'"),
            '((a = hello) OR ((b = helloworld) AND (c = hi)))')

        self.assertEqual(
            self.ptest(whereExpression,
                       "a = 'hello' and b = 'helloworld' or c = 'hi'"),
            '(((a = hello) AND (b = helloworld)) OR (c = hi))')


        self.assertEqual(
            self.ptest(whereExpression,
                       "a = 'hello' and b = 'helloworld' and c = 'hi'"),
            '(((a = hello) AND (b = helloworld)) AND (c = hi))')



        self.assertEqual(
            self.ptest(whereExpression,
                       "not a = 'hello'"),
            '(NOT (a = hello))')

    def testIn(self):
        self.assertEqual(
            self.ptest(whereExpression,
                       "a in ('hello', 'goodbye')"),
            '((a = hello) OR (a = goodbye))')
        


if __name__ == '__main__':
    unittest.main(defaultTest = "ParserTestCase")
