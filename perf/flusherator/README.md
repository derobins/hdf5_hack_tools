# Flusherator

This program was designed to generate a LOT of dirty metadata
so I could investigate a slowdown in H5Xrefresh() between
1.12.0 and later versions of the library. It could also be
used to investigate dirty metadata performance in general.

There are two programs, setup and flusherator, which can be
built by simply running h5cc over their source files. The
sizes in flusherator.h can be used to adjust the amount
of dirty metadata generated.

Run setup first to create the datasets, then run the
flusherator to write a bunch of data to the file and
flush/refresh. The flusherator program can be called many
times without re-running setup.
