---
layout: post
title:  "scalafmt in Neovim"
date:   2018-04-30 23:20:00 +0100
categories: scala formatting vim neovim
---

At [ASI Data Science][ASI], where I work as an engineer developing
[SherlockML][SherlockML], our data science platform, we write most of our
backend services in [Scala][Scala]. To save on time spent discussing code
style, we're trying out autoformatting of our code with [scalafmt][scalafmt],
with a configuration that reasonably closely reflects our current style.

Below are the steps I took to configure [Neovim][Neovim], the main editor I
use, to automatically format Scala code with scalafmt on save. These
instructions are written for use on Mac OS - on other systems you'll need to
translate to use the appropriate package manager and init system.

## 1. Install nailgun and coursier

Install nailgun and coursier with [Homebrew][Homebrew]:

```sh
brew install nailgun coursier
```

## 2. Install scalafmt with coursier

With coursier, you can now install scalafmt and create an executable running
the scalafmt service in nailgun:

```sh
coursier bootstrap \
  --standalone com.geirsson:scalafmt-cli_2.12:1.5.1 \
  -r bintray:scalameta/maven \
  -o /usr/local/bin/scalafmt_ng \
  -f --main com.martiansoftware.nailgun.NGServer
```

> **Note:** The above command installs the latest version of scalafmt at the
> time of writing. See [the scalafmt docs][scalafmt-nailgun] for a command to
> install the most up to date version.

You can test that scalafmt is working by running the server with:

```sh
scalafmt_ng
```

and in a separate shell run

```sh
ng org.scalafmt.cli.Cli --version
```

## 3. Set up scalafmt server

We don't want to have to manually run the scalafmt server, so to have Mac OS
run it as a service, create the following file in
`~/Library/LaunchAgents/nailgun.scalafmt.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>KeepAlive</key>
  <true/>
  <key>Label</key>
  <string>nailgun.scalafmt</string>
  <key>Program</key>
  <string>/usr/local/bin/scalafmt_ng</string>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

and enable the service with:

```sh
launchctl load -w ~/Library/LaunchAgents/nailgun.scalafmt.plist
```

## 4. Configure Neovim

Install neoformat with your favourite plugin manager. For example, with
[vim-plug], add to `~/.config/nvim/init.vim`:

```vim
Plug 'sbdchd/neoformat'
```

then reopen Neovim and run `:PlugInstall`.

In `~/.config/nvim/init.vim`, configure neoformat to use the scalafmt server
with:

```vim
let g:neoformat_scala_scalafmt = {
        \ 'exe': 'ng',
        \ 'args': ['org.scalafmt.cli.Cli', '--stdin'],
        \ 'stdin': 1,
        \ }
```

and optionally configure it to autoformat on save by adding:

```vim
autocmd BufWritePre *.{scala,sbt} Neoformat
```

[ASI]: https://asidatascience.com/
[SherlockML]: https://sherlockml.com/
[Scala]: https://www.scala-lang.org/
[scalafmt]: http://scalameta.org/scalafmt/
[Neovim]: https://neovim.io/
[Homebrew]: https://brew.sh/
[scalafmt-nailgun]: http://scalameta.org/scalafmt/#Nailgun
[vim-plug]: https://github.com/junegunn/vim-plug
