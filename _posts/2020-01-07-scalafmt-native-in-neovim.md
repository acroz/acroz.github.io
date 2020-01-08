---
layout: post
title:  "scalafmt in Neovim with scalafmt-native"
date:   2020-01-07 18:07:00 +0000
tags: [Scala, Code Formatting, Vim, Neovim]
---

I previously wrote [a post]({% post_url 2018-04-30-scalafmt-in-neovim %}) on
setting up [scalafmt] to autoformat [Scala] code in [Neovim]. That guide used
nailgun to help keep scalafmt fast to run, however my setup was a bit flaky and
frequently broke. Fortunately, scalafmt [now provides native binaries compiled
with GraalVm][scalafmt-native], which starts up and runs quickly enough that we
don't need to use the more complex nailgun setup. This blog post provides an
updated guide on using scalafmt in Neovim with scalafmt-native.

## 1. Install scalafmt-native

Follow the [scalafmt docs][scalafmt-native] to install scalafmt-native.

```sh
VERSION=2.3.3-RC1
INSTALL_LOCATION=/usr/local/bin/scalafmt-native
curl https://raw.githubusercontent.com/scalameta/scalafmt/master/bin/install-scalafmt-native.sh | \
  sh -s -- $VERSION $INSTALL_LOCATION
```

`scalafmt-native` should then be available in the terminal. Test it with:

```sh
scalafmt-native --help
```

## 2. Configure Neovim

With `scalafmt-native` installed, configure Neovim to automatically apply
scalafmt formatting to our Scala source files.

Install neoformat with your favourite plugin manager. For example, with
[vim-plug], add to `~/.config/nvim/init.vim`:

```vim
Plug 'sbdchd/neoformat'
```

then reopen Neovim and run `:PlugInstall`.

In `~/.config/nvim/init.vim`, configure neoformat to use `scalafmt-native`
with:

```vim
let g:neoformat_scala_scalafmt = {
        \ 'exe': 'scalafmt-native',
        \ 'args': ['--stdin'],
        \ 'stdin': 1,
        \ }
```

Finally, to configure Neovim to automatically apply formatting to Scala files
on save, add the following line to `~/.config/nvim/init.vim`:

```vim
autocmd BufWritePre *.{scala,sbt} Neoformat
```

[scalafmt]: http://scalameta.org/scalafmt/
[Scala]: https://www.scala-lang.org/
[Neovim]: https://neovim.io/
[scalafmt-native]: https://scalameta.org/scalafmt/docs/installation.html#native-image
[vim-plug]: https://github.com/junegunn/vim-plug
