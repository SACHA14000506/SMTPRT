# SMTPRT

# Overview
SMTPRT is a novel performance regression testing framework designed for SMT (Satisfiability Modulo Theories) solvers. It addresses the limitations of current performance testing methods by efficiently detecting and localizing performance regressions across various SMT solver theories. Using genetic algorithms (GAs), SMTPRT guides the search for performance regression-inducing test cases and introduces an optimized localization technique to identify the responsible commits faster and more accurately.

# Key Features
General-Purpose Testing: Designed to work across multiple SMT solver theories.

Efficient Detection: Utilizes genetic algorithms for effective test case generation.

Optimized Localization: Filters irrelevant commits using code coverage and rapidly locates the responsible commit via a bisecting algorithm.
