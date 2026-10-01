# Implementing A Temporal Reasoner Based On Behavioral Profiles
**Note:** You are encouraged, but not required, to work on this assignment in groups of two. More than two students per group are not allowed.

In this assignment, you are tasked to implement a temporal reasoner that can check whether *traces* of event data satisfy so-called *behavioral profiles*.

## Background
Before starting the assignment, get an idea of the abstractions that you will work with--traces and behavioral profiles--and how they can be applied.

### Traces 
A trace is a sequence of events that are triggered by activity executions.
For example, in an organization a purchase may be first requested, and then approved, after which a purchase order is created; this ordering of events is important for compliance reasons.
Consider that the activities  `a`, `b`, `c` and `d`, can trigger events.
Then, we may have traces such as
`<a, b, c>`,
`<c, a, d>`,
`<b, c, c, d>`,
et cetera. 
In the first trace, the intuitive reading is that "first `a` was triggered, then `b`, then `c`.
We assume traces are finite.
In practice, each activity may describe the execution of a specific task of work in an organization (such as "purchase approved"), or for the update of a business object in a database (such as "stock level decreased by at least `X`").

### Behavioral Profiles
In many use-cases, it is important to check whether sets of traces satisfy given temporal constraints.
This is often called *conformance checking*.
One way to specify temporal constraints reflecting expected trace behavior is with *behavioral profiles*.
Behavioral profiles are matrices equivalent to a binary relation on $\cal A \times A$, where $\cal A$ is the set of activities, i.e., in our example $\cal A := \{a, b, c, d\}$.
Below is an example of a behavioral profile.

```
-  a   b   c   d
a  -   ->  ->  -
b  <-  -   ||  ->
c  <-  ||  -   ->
d  -   <-  <-  -
```

As we can see, we have the four symbols `->`, `<-`, `||` and `-` that may relate two activities (let us call them `x` and `y`), which we may intuitively read as follows:

* `x -> y`: `x` may directly be followed by `y`, same as `y <- x`.

* `x <- y`: `y` may directly follow `x`, same as `y -> x`.

* `x || y`: `x` and `y` may follow each other, same as "`x -> y` and `y -> x`".

* `x - y`: `x` cannot follow `y` and `y` cannot follow `x`. Note that in the example, an activity is related to itself only using `-`, i.e., we do not have loops.

Observe that because the first three relations can be expressed using `->` only and `-` can be expressed by absence of `->`, we technically require only one relation.
Also, it is sufficient to consider only entries on and above the matrix' main diagonal.

However, these symbols do not yet have a precise *semantics* assigned to them.
In order to do this, you will need to implement an algorithm that turns the matrix into a set of linear temporal logic (LTL) formulas.
In addition, we generate regular expressions (RegExps) that allow for a straightforward operationalization (execution) of the formulas.
Note that below, we use `->` to denote LTL's `implication` operator, whereas `N` denotes `next` and `G` denotes `globally`.
**Important:** this means that the intended semantics of `->` is fundamentally different between LTL and behavioral profiles.

1. **Collect start activities**:  
  Generate the following constraint for all activities `x_1, ..., x_n` that do not have a predecessor:  
  LTL: `G(START -> (x_1 v ... v x_n))`; RegExp: `^(x_1|...|x_n)`.  
  **Note:** here, `START` is a synthetic event that is assumed to coincide with the first event of a given trace; however, this is only required in case of LTL-based verification, and not when regular expressions are used.

2. **Collect directly-follows relationships**:  
  For each activity `x` that has at least one successor, generate the following constraint, given successors `y_1 ... y_n`:  
  LTL: `G(x -> N(y_1 v ... v y_n))`; RegExp: `^[^x]*(x(y_1|...|y_n)[^x]*)*[^x]*$`.  
  **Note:** you may wonder why the regular expression is so "complicated". Here, we clearly see that
  LTL has some advantages as a notation over RegExp and is more intuitive than regular expressions
  for reasoning about trace data. Also, LTL can be theoretically faster, as it does not require the
  expressivity of the Kleene star `*`. However, the *reasoner* you will implement relies on regular
  expressions, as these can be straightforwardly executed by most mainstream programming languages.

3. **Collect end activities**:  
  Generate the following constraint for all activities `x_1, ..., x_n` that do not have a successor.  
  LTL: `G((x_1 v ... v x_n) -> END)`; RegExp: `(x_1|...|x_n)$` and in addition (not alternatively) `^(?!.*((x_1|...|x_n)(x_1|...|x_n)).*$)`.  
  **Note:** here, `END` is a synthetic event, analogous to `START`.


## Task Description
Your primary task is to implement a parser and reasoner; in addition, you have to write a brief report.

### Implementation
Your **implementation** task is the following.
Write a tool that, given a behavioral profile (matrix), parses the matrix and turns it into
1. a set of LTL formulas and regular expressions;
2. supports the regular expressions on trace data.

We have defined test cases that check whether Sub-tasks 1 and 2 have been executed correctly.
The test cases have been implemented in [pytest](https://docs.pytest.org/en/stable/).
However, the tests can call any tool---in this boilerplate repository another python tool---via a command line interface.
This means that you can easily adjust them to call a tool that you have implemented in a programming language of your choice.
For this, adjust the `parser_base_command` and `reasoner_base_command` variables in the `conf.py` file of the `tests` directory.
Important is that you keep the expected input and output format, which is JSON-based and can be inferred from the corresponding test case input/output-tuples.

### Expected Input

The parser should be executable as follows, for example:

`python parser.py ./tests/matrix_1.json RegExp`

and

`python parser.py ./tests/matrix_1.json LTL`,

where `python` and `parser.py` are picked up from the `parser_base_command`
variable in the configuration file, `./tests/matrix_1.json` points to the
parser's input, and `RegExp`/ `LTL` specifies the output format.


The parser takes a JSON object (read from a file) as input:

```
{
    "a": ["-" , "->", "->", "-" ],
    "b": ["<-", "-" , "-" , "->"],
    "c": ["<-", "-" , "-" , "->"],
    "d": ["-" , "<-", "<-", "-" ]
}
```

The JSON object models the behavioral profile.
Note that a key assumption is that the activities are alpha-numerically ordered:
the first entry in a given array relates to the first activity given this order,
and so forth.

The reasoner should be executable as follows, for example:

`python reasoner.py ./tests/matrix_1.json ./tests/traces_1.json`,

where `./tests/matrix_1.json` is (again) the behavioral profile (matrix)
and `./tests/traces_1.json` is a JSON list of lists, where each list is a trace, e.g.:

```
[
    ["a", "b", "d"],
    ["a", "c", "d"],
    ["b", "c", "d"],
    ["a", "b", "a"],
    ["a", "b", "d", "a"],
    ["a", "b", "c", "d"]
]
```

### Expected Output
The expected output of the parser are LTL- and RegExp-based constraints, provided as a JSON array.

Examples for LTL-based constraints are:

```
G(START -> (a))
G(a -> N(b v c))
G((d) -> END)
```

Examples for RegExp-based constraints are:

```
^(a)
^[^a]*(a(b|c)[^a]*)*[^a]*$
(d)$
^(?!.*((d)(d)).*$)
```

Note that the constraints above are **not** the complete constraints of the initial matrix.
Also note that following the **exact** syntax of the examples matters in order to pass the tests.
This should not be any problem, because you can easily check the test cases and adjust your parser
in case syntax nuances lead to test failures.

The expected output of the reasoner are traces that are labelled `true` in case all constraints are satisfied
and `false` otherwise, for example:

```
{
  "abd": true,
  "acd": true,
  "bcd": false,
  "aba": false,
  "abda": false,
  "abcd": false
}
```

Note that the traces are joined to a string and that the returned object is a JSON object (not a Python dictionary).
Again, you can check the test implementation to learn more about the expected output.

### Boilerplate Code and Tests
Boilerplate code is provided with the ``parser.py`` and ``reasoner.py`` files.
You can either adjust these files or implement alternatives.
In the latter case, you may need to adjust ``conf.py`` in the ``tests`` directory,
as mentioned above.
The repository contains two test files in the ``tests`` directory,
for parser and reasoner, respectively.
Also, there are six example matrices (behavioral profiles) that are used in the tests.
Each matrix comes with its own trace file, for the sake of simplicity.
All tests need to pass and will be executed on Labres upon submission.
You execute the tests by running `pytest` in the project's root directory.
This requires that `pytest` is installed, of course.

### Report
In addition to the implementation task, you need to write a **report** describing your approach:

1. Briefly explain the problem in your own words.
2. Describe how your implementation works.
3. Argue informally for the correctness of your implementation.  
 **Stretch Task 1:** the reasoner gives behavioral profiles a *semantics*. You can argue why giving it a slightly different semantics may be better in some cases. Note that *stretch tasks* are optional.
4. Report on the (successful) execution of test cases.  
**Stretch Task 2:** you can conduct additional evaluations, e.g., with respect to run-time.
5. Describe what challenges you have encountered and what you would have done differently in hindsight.
6. Describe in ~2-3 sentences how you split your work.

The length of the report should be around 3-5 pages, incl. the title page.
A report template, incl. a boilerplate report structure, is available at [https://www.overleaf.com/read/ctznmfxkmyyh#ec38b6](https://www.overleaf.com/read/ctznmfxkmyyh#ec38b6).

## Submission
Submit your code and report on Labres.
Only submit files that you actually need to change:

* The parser: ``parser.py`` or a similar file in a language other than Python;
* The reasoner: ``reasoner.py`` or a similar file in a language other than Python;
* Optionally, ``conf.py``;
* Obviously, the report.

Try to not use more files than necessary and don't pull in extra dependencies.

