---
layout: post
title:  "Navigating a sea of repos"
date:   2020-07-04 14:32:00 +0100
tags:   [Python, git, System Administration]
---

From both work and personal projects, I have lots (at the time of writing, 182)
repositories cloned on my laptop. Most of these are repositories that I
contribute to, though some are other code bases that I've cloned to be able to
search more effectively with command line tools.

To help organise them in a sane way, I keep them in a directory structure that
mirrors their URLs when cloned from GitHub, Bitbucket or GitLab. For example,
they look like:

* ~/src/github.com/acroz/pylivy
* ~/src/bitbucket.org/acroz/other-repo
* ~/src/gitlab.com/organisation/group/subgroup/repo

This works well, and helps to find repositories that I know are stored in a
particular Bitbucket organisation, for example, but works less well when I'm
less sure of that repo's location. Even when I do know the location, there's
still often a lot of bashing the tab key to complete nested directories.

To save time with this, I've set up a function in my shell that fuzzily matches
the git repositories. This glues together 3 parts:

1. Generate a list of all repos with `find` or similar
2. Fuzzily match on this list of repos with [`fzy`][fzy]
3. Change directory to the selected repo

## Old solution with `find`

Prior to using GitLab repositories, I used the fact that all repositories were
exactly two levels below `~/src` to generate the list of repositories:

```sh
find ~/src -type d -mindepth 2 -maxdepth 2
```

However, since GitLab can have nested organisations, the depth of the
repository root relative to `~/src` can no longer be guaranteed. I was able to
generate a `find` command that would identify git repositories using the fact
that they contain a `.git` directory, but it was really slow because it's
searching the contents of all the repositories when it doesn't need to:

```sh
find ~/src -type d -name .git | sed 's/\/\.git$//g'
```

On my my current source directory, this takes 27 seconds to run!

## New solution: `git-find-repos`

To more efficiently search my local directories, I wrote
[a simple CLI tool][git-find-repos] that does a recursive search of a
directory, printing out git repositories. As it's able to stop traversing down
a directory tree as soon as it encounters a `.git` directory, it's much faster
(0.26 seconds instead of 27).

You can check out `git-find-repos` for yourself [on GitHub][git-find-repos].
Installation is easy with `pip` or `pipx`:

```sh
pipx install git-find-repos
```

By default, `git-find-repos` searches the current directory recursively.
Alternatively, you can specifiy a particular path:

```sh
git-find-repos ~/src
```

You can also use `git-find-repos` as if it were a subcommand of `git` (thanks
to my colleague Víctor Zabalza [for this suggestion][rename-suggestion]):

```sh
git find-repos ~/src
```

## Putting it all together

With `git-find-repos`, I'm able to put together my convenience shell function
as desired. In my `.zshrc`, I define the following function:

```zsh
function repo {
    initial_query=$1
    dest=$(git find-repos ~/src | fzy -q "$initial_query" -l 20) && cd "$HOME/src/$dest"
}
```

Now, all I need to do to navigate to a repo is run `repo` in the shell, type
enough of the name for it to match with `fzy`, then hit enter. If a match is
found, the `repo` function will change my directory there.

[fzy]: https://github.com/jhawthorn/fzy
[git-find-repos]: https://github.com/acroz/git-find-repos
[rename-suggestion]: https://github.com/acroz/git-find-repos/issues/1
