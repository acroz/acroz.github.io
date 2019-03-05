---
layout: post
title:  "scalafmt in Neovim"
date:   2018-04-30 23:20:00 +0100
tags: scala formatting vim neovim
---

At [Faculty], where I work as an engineer developing [our data science
platform][Faculty platform], we write most of our backend services in [Scala].
To save on time spent discussing code style, we're trying out autoformatting of
our code with [scalafmt], with a configuration that reasonably closely reflects
our current style.

scalafmt is [relatively easy to set up in IntelliJ][scalafmt in IntelliJ], a
popular IDE for Java and Scala, however I and many on our development team use
[Neovim] as our primary code editor. This article details the steps we took to
get Neovim to apply scalafmt to Scala source code automatically on save.

These instructions are written for use on Mac OS – on other systems you’ll need
to translate to use the appropriate package manager and init system.

## 1. Install nailgun

As responsiveness is important when running scalafmt from an editor, it’s
recommended to run scalafmt through nailgun. Nailgun keeps scalafmt running on
a local server to avoid paying a penalty to start up the JVM on each run.

To install nailgun with [Homebrew]:

```sh
brew install nailgun
```

## 2. Install scalafmt with coursier

If you don’t already have coursier, install it with Homebrew:

```sh
brew install --HEAD coursier/formulas/coursier
```

With coursier, install scalafmt and create an executable running the scalafmt
service in nailgun:

```sh
coursier bootstrap \
  --standalone com.geirsson:scalafmt-cli_2.12:1.5.1 \
  -r bintray:scalameta/maven \
  -o /usr/local/bin/scalafmt_ng \
  -f --main com.martiansoftware.nailgun.NGServer
```

Create an alias to run the scalafmt CLI through nailgun with:

```sh
ng ng-alias scalafmt org.scalafmt.cli.Cli
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
ng scalafmt --version
```

## 3. Create scalafmt service

We don’t want to have to manually run the scalafmt server every time we start
the computer, so to have Mac OS run it as a service, create the following file
in `~/Library/LaunchAgents/nailgun.scalafmt.plist`:

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

Finally, we want to configure Neovim to automatically apply scalafmt formatting
to our Scala source files.

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
        \ 'args': ['scalafmt', '--stdin'],
        \ 'stdin': 1,
        \ }
```

Finally, to configure Neovim to automatically apply formatting to Scala files
on save, add the following line to `~/.config/nvim/init.vim`:

```vim
autocmd BufWritePre *.{scala,sbt} Neoformat
```

[Faculty]: https://faculty.ai/
[Faculty platform]: https://faculty.ai/products-services/platform/
[Scala]: https://www.scala-lang.org/
[scalafmt]: http://scalameta.org/scalafmt/
[scalafmt in IntelliJ]: https://scalameta.org/scalafmt/docs/installation.html#intellij
[Neovim]: https://neovim.io/
[Homebrew]: https://brew.sh/
[scalafmt-nailgun]: https://scalameta.org/scalafmt/docs/installation.html#nailgun
[vim-plug]: https://github.com/junegunn/vim-plug
