---
title: Automerge Dependabot PRs on GitHub
date: 2022-07-07
tags:
    - GitHub
---

Whether I'm trying out a new tool or just prototyping with a familiar stack, I usually
create a new project on GitHub and run all the experiments there. Some examples of these
are:

* [rubric][1]: linter config initializer for Python
* [exert][2]: declaratively apply converter functions to class attributes
* [hook-slinger][3]: generic service to send, retry, and manage webhooks
* [think-async][4]: exploring cooperative concurrency primitives in Python
* [epilog][5]: container log aggregation with Elasticsearch, Kibana & Filebeat

While many of these prototypes become full-fledged projects, most end up being just
one-time journies. One common theme among all of these endeavors is that I always
include instructions in the `readme.md` on how to get the project up and running—no
matter how small it is. Also, I tend to configure a rudimentary CI pipeline that runs
the linters and tests. GitHub actions and [Dependabot][6] make it simple to configure a
basic CI workflow. Dependabot keeps the dependencies fresh and makes pull requests
automatically when there's a new version of a dependency used in a project.

Things can get quickly out of hand if you've got a large collection of repos where
the automated CI runs periodically. Every now and then, I get a sizable volume of PRs in
these fairly stale repos that I still want to keep updated. Merging these manually is
a chore. Luckily, there are multiple [ways][7] that GitHub offers to automatically merge
PRs. The workflow that is documented here is the one I happen to like the most. I also
think that this process leads to the path of the least surprise. Instead of depending on
a bunch of GitHub settings, we'll write a GitHub action [worflow][8] to automate the
process.

First, you'll need to turn on the auto-merge option from the repository settings. To do
so, go to the repo's *settings* tab and turn on the *Allow auto-merge* option from the
*Pull Requests* section:

![image](https://user-images.githubusercontent.com/30027932/178368689-4766f2d3-86ed-4287-b058-6edfeecba66a.png)

Now, you probably don't want to mindlessly merge every pull request Dependabot throws at
you. You most likely want to make sure that a pull request triggers certain tests and
it'll be merged only if all of those checks pass. To do so, you can turn on
[branch protection][9]. From the *settings* panel, select *Branches* on the left panel:

![image](https://user-images.githubusercontent.com/30027932/177646826-f07b6ad0-9df7-42cd-ab70-c74a1ec31059.png)

Once you've selected the tab, add a branch protection rule to the target branch against
which Dependabot will send the pull requests:

![image](https://user-images.githubusercontent.com/30027932/177646967-36ba6b6d-861f-44d6-9a91-b5f5f3a3ce45.png)

In this case, I'm adding the protection layer to the `main` branch. I've turned on the
*Require status checks to pass before merging* toggle and added the `build` step to the
list of status checks that are required. Here, you can select any job from your CI files
in the `.github/workflows` directory:

![image](https://user-images.githubusercontent.com/30027932/177647370-012d0162-d80b-4f12-9ac7-b7a6da024735.png)

Once this is done, you can drop the following CI file in the `.github/workflows`
directory of your repo. It's the same [file][10] that's currently living inside this
site's CI folder.

```yaml
# .github/workflows/automerge.yml

name: Dependabot auto-merge

on: pull_request

permissions:
  contents: write
  pull-requests: write  # Needed if in a private repository

jobs:
  dependabot:
    runs-on: ubuntu-latest
    if: ${{ github.actor == 'dependabot[bot]' }}
    steps:
      - name: Enable auto-merge for Dependabot PRs
        run: gh pr merge --auto --merge "$PR_URL"
        env:
          PR_URL: ${{github.event.pull_request.html_url}}
          # GitHub provides this variable in the CI env. You don't
          # need to add anything to the secrets vault.
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

From now on, every time Dependabot sends a merge request, the checks will be triggered
and if all the mandatory checks pass, the `automerge.yml` workflow will merge it into
the target branch.

[1]: https://github.com/rednafi/rubric
[2]: https://github.com/rednafi/exert
[3]: https://github.com/rednafi/hook-slinger
[4]: https://github.com/rednafi/think-async
[5]: https://github.com/rednafi/epilog
[6]: https://docs.github.com/en/code-security/dependabot/dependabot-security-updates/configuring-dependabot-security-updates
[7]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request
[8]: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions#enable-auto-merge-on-a-pull-request
[9]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
[10]: https://github.com/rednafi/reflections/blob/master/.github/workflows/automerge.yml
