Glossary of Terms
*****************

Time
====

cpu time
--------

The amount of CPU seconds consumed by the job.  This is the number of processors multiplied by the wall clock time
for the job.  For example, if a job that started at 00:00 and completed at 00:01 and was assigned a single processor,
it would have a cpu time of 1 minute.  However, another job that started at 00:00 and finished also at 00:01 but ran
on ten processors, it would have a wall clock time of one minute, and a cpu time of ten minutes.

wall clock time
---------------

The amount of time that the job executed for, regardless of the number of processors requested.  For example if a job
starts at 00:00 and finished at 00:10 it would have a wall clock time of ten minutes regardless of the number of
processors used.  Wall clock time does not include time spent pending.

pend time
---------

The amount of time that a job spends between the moment it was submitted into the batch scheduling system and the moment
the job starts to run.  For example, if a job is submitted at 00:00 and starts executing at 00:05, it would have a pend
time of five minutes