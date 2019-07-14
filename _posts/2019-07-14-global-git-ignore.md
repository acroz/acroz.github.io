---
layout: post
title:  "Global Git Ignores"
date:   2019-07-14 15:08:00 +0000
tags: [git]
---

Git has a great feature that allows you to avoid committing lots of unnecessary
files to your repository. By creating a file called `.gitignore` in your
repository, you can declare that files and directories which match certain name
patterns should never be added to the repository. This means that, for example,
when running Python code from a repostitory, all of the `.pyc` files generated
by Python can be excluded from commits, but will also not be shown when running
commands like `git status` which shows you what local files you have that are
uncommitted.

A typical `.gitignore` file for a Python project might look like:

```
*.py[co]
__pycache__/
build/
dist/
.eggs/
*.egg-info/
```

which ignores a variety of files and directories created when running Python
code or building it into packages.

One thing I do not tend to include in my project `.gitignore` files, however,
is editor-specific ignores. Such ignores are hard to test as different people
use different editors, and can become increasingly idiosyncratic and hard to
maintain as more developers get involved in a project.

Instead, I prefer to maintain a 'global' git ignore file that handles editor-
or system-specific files that are both common across many projects and likely
to be different for different developers.

## Creating a global git ignore file

To create a global git ignore, you need to configure it in your global git
configuration. This will likely be either `~/.config/git/config` or
`~/.gitconfig`. If you do not have one of these files already, just create one
of them. (I prefer to use the former to reduce clutter in my home directory.)

In your config file, create an entry like the following:

```ini
[core]
    excludesfile = ~/.config/git/ignore
```

This configures git to read ignore rules from the specified location. In the
case that your config file is at `~/.gitconfig`, you may want to use the
corresponding `~/.gitignore` location instead of that in the example above.

Once you've added this configuration, all you need to do is create a file at
the configured location with the ignore rules you want applied to all projects.

My global ignore file currently looks like:

```
.python-version  # Config for local Python environment with pyenv
.DS_Store  # Cruft created by macOS
.ipynb_checkpoints  # Working directory created by Jupyter
```

The editor I use, [Neovim], does not create temporary files in the working
directory, however others do. [IntelliJ] and related tools like [PyCharm]
create an `.idea` project directory inside the project repository, which I'd
recommend adding to your global git ignore.

[Neovim]: https://neovim.io/
[IntelliJ]: https://www.jetbrains.com/idea/
[PyCharm]: https://www.jetbrains.com/pycharm/
