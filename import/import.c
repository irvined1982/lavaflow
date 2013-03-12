# Copyright 2011 David Irvine
# 
# This file is part of LavaFlow
#
# LavaFlow is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.
#
# LavaFlow is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with LavaFlow.  If not, see <http://www.gnu.org/licenses/>.
#
#include <lsf.h>
#include <lsbatch.h>

int main(int argc, char **argv){
	struct eventRec *log;
	FILE *log_fp;
	int lineNum = 0;
	struct bhistReq *reqPtr;
	struct jobFinishLog *finishJobrec;
	struct jobNewLog *newJobrec;

	 if (lsb_init(argv[0]) <0) {
		 lsb_perror("lsb_init");
		 exit(-1);
	 }
	log_fp=fopen("/tmp/stats.acct", "r");
	while(1){
		if ((log = lsb_geteventrec(log_fp, &lineNum)) != NULL) {
			printf("Line: %d, Type: %d, %d\n",lineNum, EVENT_JOB_NEW,log->type);
			switch (log->type) {
				case EVENT_JOB_FINISH:
					finishJobrec = &(log->eventLog.jobFinishLog);
					printf("%s\n",finishJobrec->userName);
				case EVENT_JOB_NEW:
					printf("New\n");
					newJobrec=&(log->eventLog.jobNewLog);
					printf("%d\n",newJobrec->jobId);
			}
		}
	}
	return 0;
}
