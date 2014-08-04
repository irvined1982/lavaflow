About
=====

LavaFlow was created out of my desire to understand cluster usage patterns. It started life as a series of python
scripts that simply parse the various log files and printed statistics. Over time, as the data grew, and the queries
become more complex, a new approach was needed, and LavaFlow was born.

In 2011, it simply produced some static web pages using Flot, from scheduler log files. Now it has a generic data
format and can read data from multiple scheduling systems. In the future, I hope to add support for Nagios, and other
 metric gathering tools to enable better analysis of events external to the scheduling system and their effect on the
 cluster.

The key to any statistical analysis tool is that it has to answer questions that people ask, and as I discover new
questions, the tool will hopefully evolve to answer them.

LavaFlow is `free software <http://www.gnu.org/licenses/gpl.html>`_.
