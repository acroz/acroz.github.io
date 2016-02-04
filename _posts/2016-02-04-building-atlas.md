---
layout: post
title:  "Building ATLAS"
date:   2016-02-04 00:50:00 +0100
categories: build numerics sysadmin
---
Today I attempted to build [ATLAS (Automatically Tuned Linear Algebra
Software)], an optimised linear algebra package which finely tunes itself to
your system during the build process. While [ATLAS] is available through many
package managers, these non-optimised builds miss out on much of the benefit of
using this library.

I found building [ATLAS] to be more involved than many other related packages
like [LAPACK], however with a little perserverance it was achievable.

## Disable CPU Throttling

During its extensive tuning in the build process, [ATLAS] needs to perform a
lot of profiling. For this precise profiling to work requires the disabling of
CPU throttling, the process whereby modern CPUs reduce their clock frequency
while idle to save power.

I was able to achieve this on my system (running Arch Linux on a computer with
twin Intel(R) Xeon(R) E5-2630s) through use of the cpupower package. First,
install the package:

{% highlight bash %}
sudo pacman -S cpupower
{% endhighlight %}

and then assign the "performance" power governor:

{% highlight bash %}
sudo cpupower frequency-set -g performance
{% endhighlight %}

This unfortunately did not work by itself on my processors due to [an apparent
problem with the intel\_pstate power governor][jousse.org]. To resolve this,
[restart the computer with the additional kernel parameter][grubkernel]
``intel_pstate=disable``, and then execute

{% highlight bash %}
sudo modprobe acpi-cpufreq
{% endhighlight %}

to enable the generic governors. Set the performance governor as above, then
proceed with building [ATLAS].

## Avoiding Hyperthreading

For reasons [they are more adept to explain][ATLAS HT], the [ATLAS] authors
strongly discourage the use of hyperthreading. To disover the IDs of unique
cores on my sytem, I discovered the great [likwid] package. To install it:

{% highlight bash %}
git clone https://github.com/RRZE-HPC/likwid/
cd likwid
make
sudo make install
{% endhighlight %}

Use the ``likwid-topology`` command to print, among other information, a table
of all the hyperthreads and their mappings to physical sockets and cores. This
allowed me to determine that threads 0-11 (out of 0-23) would map on to unique
cores.

## Build ATLAS

We are now ready to build [ATLAS] itself. Download both it and the latest
[LAPACK] release, unpack [ATLAS] and create a build directory. To build the
software, first run the configure command in the build directory:

{% highlight bash %}
cd build
/path/to/ATLAS/configure \
    --with-netlib-lapack-tarfile=/path/to/downloaded/lapack-x.x.x.tgz \
    --force-tids="NTHREAD T0 T1 T2 .. TN-1" \
    -D c -DPentiumCPS=MHZ \
    -v 2
{% endhighlight %}

The first argument points to the [LAPACK] tarball you downloaded, the second
lists the IDs of the unique threads from the step above, the next two arguments
make the build system use a more accurate timer during tuning (replace MHZ with
your clock speed in MHz, and do not use these options if the build will be
competing for resources), and the final argument sets the maximum level of
verbosity.

Once the configuration is complete, run the build with

{% highlight bash %}
make
{% endhighlight %}

When complete, consider running the tests:

{% highlight bash %}
make check   # Test serial routines
make ptcheck # Test parallel routines
make time    # Compare performance against a reference
{% endhighlight %}

and if desired, install to the system location with:

{% highlight bash %}
sudo make install
{% endhighlight %}

[ATLAS]:      http://math-atlas.sourceforge.net/
[ATLAS HT]:   http://math-atlas.sourceforge.net/atlas_install/node21.html
[LAPACK]:     http://www.netlib.org/lapack/
[jousse.org]: http://vincent.jousse.org/tech/archlinux-compile-lapack-atlas-kaldi/
[grubkernel]: http://askubuntu.com/a/19487/293498
[likwid]:     https://github.com/RRZE-HPC/likwid/
