---
title: Git revision specifiers redux
date:
tags:
    - Git
---

Only recently, I found out that the identifiers used in Git commands, such as
`git log HEAD~1`, `git checkout branch_name>`, or `git diff <sha-1>`, have a generic name.
These notations—`HEAD~1`, `branch_name`, or `<sha-1>`—are called revision parameters. Over
the years, I’ve picked them up without paying much attention and never really peeked into
the docs to see all the available options.

It turns out there's a lot you can do with revision parameters. You can grab a single
commit, a range of commits, commits reachable from one branch but not another, commits on a
different parent in a merge commit, and more. They're thoroughly documented here. However, I
find the documentation a bit bleh.

Plus, some of the specifier rules can get quite complicated, making it easy to get confused
by notations like `main..feature_branch`, `main...feature_branch`, `@`, `@^main`, `@~1`,
`@^^~2`, `HEAD^^`, or `HEAD~2`. So, I wanted to expand on a few of my frequently used
commands that use these revision specifiers in ways that might not be obvious without
frantically grokking the docs or GPT-ing your way through.
