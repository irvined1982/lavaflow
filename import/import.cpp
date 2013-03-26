#include <string>
#include <sstream>
#include <iostream>
#include <err.h>
extern "C" { 
#include <lsbatch.h>
#include <lsf.h>
}


using namespace std;
	std::string int_to_str(int value){
		std::stringstream ss;
		ss<<value;
		return ss.str();
	}

	int addJString(std::string &data, const char *name, const char *value, int comma){
		data+="\"";
		data+=name;
		data+="\":";
		data+=value;
		if (comma){
			data+=",";
		}
		data+="\n";
		return 0;
	}
	int addJFloat(std::string &data, const char *name, float value, int comma){
		std::stringstream ss;
		ss<<value;
		data+="\"";
		data+=name;
		data+="\":";
		data+=ss.str();
		if (comma){
			data+=",";
		}
		data+="\n";
		return 0;
	}
	int addJTime(std::string &data, const char *name, time_t value, int comma){
		std::stringstream ss;
		ss<<value;
		data+="\"";
		data+=name;
		data+="\":";
		data+=ss.str();
		if (comma){
			data+=",";
		}
		data+="\n";
		return 0;
	}
	int addJInt(std::string &data, const char *name, int value, int comma){
		std::stringstream ss;
		ss<<value;
		data+="\"";
		data+=name;
		data+="\":";
		data+=ss.str();
		if (comma){
			data+=",";
		}
		data+="\n";
		return 0;
	}
	void addRUsage(std::string &data, const char *name, const float value, const char * desc, int comma){
		data+="{\n";
		addJString(data,"name",name,1);
		addJString(data,"description",desc,1);
		addJFloat(data,"value",value,0);
		data+="}";
		if (comma){
			data+=",";
		}
		data+="\n";
	}
int main( int argc, char *argv[] ) {
	std::string logFilePath;
	std::string clusterName;
	std::string url;
	std::string jsonData;
	int lineOne=1;
	
	struct eventRec *log;
	FILE *log_fp;
	int lineNum = 0;
	struct bhistReq *reqPtr;
	struct jobFinishLog *jf;
	struct jobNewLog *newJobrec;
	struct lsfRusage *ru;


	if (lsb_init(argv[0]) <0) {
		errx(1, "Unable to initialize LSF");
	}
	if (argc<4){
		errx(1, "Usage:\n %s <LogFile> <Cluster Name> <Url>",argv[0]  );
	}

	logFilePath=argv[1];
	clusterName=argv[2];
	url=argv[3];
	log_fp=fopen(logFilePath.c_str(), "r");
	if (log_fp==NULL){
		errx(1,"Unable to open log file: %s", logFilePath.c_str());
	}
	
	jsonData="[\n";


	while(1){
		log = lsb_geteventrec(log_fp, &lineNum);
		if (log == NULL && lsberrno==LSBE_EOF){
			break;
		}
			switch (log->type) {
				case EVENT_JOB_FINISH:
					cout << lineNum;
					cout <<"\n";
					jf = &(log->eventLog.jobFinishLog);
					// Start a new object
					jsonData+="{\n";
					addJString(jsonData, "type","job_finish",1);
					addJInt(jsonData,"job_id",jf->jobId,1);
					addJFloat(jsonData,"host_factor",jf->hostFactor,1);
					addJInt(jsonData, "user_id",jf->userId,1);
					addJInt(jsonData,"options", jf->options,1);
					
					addJInt(jsonData,"num_processors", jf->numProcessors,1);
					addJTime(jsonData,"submit_time", jf->submitTime,1);
					addJTime(jsonData,"begin_time", jf->beginTime,1);
					addJTime(jsonData,"term_time", jf->termTime,1);
					addJTime(jsonData,"start_time", jf->startTime,1);
					addJTime(jsonData,"end_time", jf->endTime,1);

					addJFloat(jsonData,"cpu_time", jf->cpuTime,1);
					addJInt(jsonData,"exit_status", jf->exitStatus,1);
					addJInt(jsonData,"max_num_processors", jf->maxNumProcessors,1);
					addJInt(jsonData,"array_index", jf->idx,1);
					addJInt(jsonData,"max_residual_mem", jf->maxRMem,1);
					addJInt(jsonData,"max_swap", jf->maxRSwap,1);
					addJString(jsonData, "requested_resources", jf->resReq,1);
					addJString(jsonData, "user_name", jf->userName,1);
					addJString(jsonData, "submit_host", jf->fromHost,1);
					
					if (jf->jStatus==JOB_STAT_DONE){
						addJString(jsonData, "job_status","Done",1);	
					}else{
						addJString(jsonData, "job_status","Exit",1);              
					}

					jsonData+="\"exit_reason\":{ \n";
					if (jf->jStatus==JOB_STAT_DONE){
						addJString(jsonData, "name", "Done", 1);
						addJString(jsonData, "description", "The task completed succesfully",1);
						addJInt(jsonData, "value", jf->exitStatus,0);
					}else if (jf->startTime<1){
						addJString(jsonData, "name", "Killed_Queue", 1);
						addJString(jsonData, "description", "The task was killed whilst still in the queue",1);
						addJInt(jsonData, "value", jf->exitStatus,0);
					}else{
						std::string tmpString;
						tmpString="Killed_Exec_";
						tmpString+=int_to_str(jf->exitStatus);
						addJString(jsonData,"name",tmpString.c_str(),1);
						addJString(jsonData, "description", "The task was killed whilst executing",1);
						addJInt(jsonData, "value", jf->exitStatus,0);
					}
					jsonData+="},\n";

					addJString(jsonData,"queue", jf->queue,1);
					addJString(jsonData,"cwd", jf->cwd,1);
					addJString(jsonData,"input_file", jf->inFile,1);
					addJString(jsonData,"output_file",jf->outFile,1);
					addJString(jsonData,"error_file,", jf->errFile,1);
					addJString(jsonData,"input_file_spool", jf->inFileSpool,1);
					addJString(jsonData,"command_spool", jf->commandSpool,1);
					addJString(jsonData,"job_file", jf->jobFile,1);
					addJString(jsonData,"job_name", jf->jobName,1);
					addJString(jsonData,"command", jf->command,1);
					addJString(jsonData,"user_name", jf->userName,1);
					addJString(jsonData,"dependency_conditions", jf->dependCond,1);
					addJString(jsonData,"pre_execution_command", jf->preExecCmd,1);
					addJString(jsonData,"email_user", jf->mailUser,1);
					addJString(jsonData,"projects", jf->projectName,1);
					addJString(jsonData,"login_shell", jf->loginShell,1);
		
					int i;
					jsonData+="\"requested_hosts\":[\n";
					if (jf->numAskedHosts>0){
						for (i=0;i<jf->numAskedHosts;++i){
							if (i>0){
								jsonData+=",\n";
							}
							jsonData+="\"";
							jsonData+=jf->askedHosts[i];
							jsonData+="\"";
						}	
					}
					jsonData+="\n],\n";
					jsonData+="\"used_hosts\":[\n";
					if (jf->numExHosts>0){
						for (i=0;i<jf->numExHosts;++i){
							if (i>0){
								jsonData+=",\n";
							}
							jsonData+="\"";
							jsonData+=jf->execHosts[i];
							jsonData+="\"";
						}	
					}
					jsonData+="\n],\n\"resource_usage\":[{\n";
					
					addJTime(jsonData,"timestamp", jf->endTime,1);
					jsonData+="\"is_summary\":true,\n\"metrics\":[\n";
					ru=&(jf->lsfRusage);
					addRUsage(jsonData,"User Time",ru->ru_utime,"User Time User" ,1);
					addRUsage(jsonData,"System Time",ru->ru_stime,"System Time Used" ,1);
					addRUsage(jsonData,"Max Shared Text",ru->ru_maxrss,"Maximum shared text size" ,1);
					addRUsage(jsonData,"Int Sh Text",ru->ru_ixrss,"Integral of the shared text size over time (in KB seconds)" ,1);
					addRUsage(jsonData,"Int Sh Mem",ru->ru_ismrss,"Integral of the shared memory size over time (valid only on Ultrix)" ,1);
					addRUsage(jsonData,"Int Unsh Data",ru->ru_idrss,"Integral of the unshared data size over time",1 );
					addRUsage(jsonData,"Int Unsh Stack",ru->ru_isrss,"Integral of the unshared stack size over time",1 );
					addRUsage(jsonData,"Page Reclaims",ru->ru_minflt,"Number of page reclaims",1 );
					addRUsage(jsonData,"Page Faults",ru->ru_majflt,"Number of page faults" ,1);
					addRUsage(jsonData,"Swapped Out",ru->ru_nswap,"Number of times the process was swapped out",1 );
					addRUsage(jsonData,"Block Input",ru->ru_inblock,"Number of block input operations" ,1);
					addRUsage(jsonData,"Block Output",ru->ru_oublock,"Number of block output operations" ,1);
					addRUsage(jsonData,"Chars R/W",ru->ru_ioch,"Number of characters read and written (valid only on HP-UX)" ,1);
					addRUsage(jsonData,"Messages Sent",ru->ru_msgsnd,"Number of System V IPC messages sent" ,1);
					addRUsage(jsonData,"Messages Rec",ru->ru_msgrcv,"Number of messages received" ,1);
					addRUsage(jsonData,"Signals Rec",ru->ru_nsignals,"Number of signals received" ,1);
					addRUsage(jsonData,"Vol Ctx Sw",ru->ru_nvcsw,"Number of voluntary context switches" ,1);
					addRUsage(jsonData,"Invol Ctx Sw",ru->ru_nivcsw,"Number of involuntary context switches" ,1);
					addRUsage(jsonData,"Exact User Time",ru->ru_exutime,"Exact user time used (valid only on ConvexOS)",0 );

					jsonData+="]\n}]}\0";
					if (!lineOne){
						jsonData=","+jsonData;
					}
					lineOne=0;
					
				case EVENT_JOB_NEW:
					newJobrec=&(log->eventLog.jobNewLog);
			}
		
	}
	jsonData+="\n]\n";
	cout <<jsonData;
	return 0;
}
