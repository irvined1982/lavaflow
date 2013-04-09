#include <string>
#include <sstream>
#include <iostream>
#include <err.h>
#include <curl/curl.h>
extern "C" { 
#include <lsbatch.h>
#include <lsf.h>
}

#define MAX_ENTRIES 10

using namespace std;
	std::string int_to_str(int value){
		std::stringstream ss;
		ss<<value;
		return ss.str();
	}

size_t write_data(void *buffer, size_t size, size_t nmemb, void *userp)
{
	return nmemb*size;
}

	void uploadData(std::string &data, std::string url){
		CURL *curl;
		CURLcode res;
		struct curl_slist *headers=NULL;
		curl_global_init(CURL_GLOBAL_ALL);
		curl = curl_easy_init();
		if(curl) {
			headers = curl_slist_append(headers, "Content-Type: application/json");
			curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers); 
			curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
			curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT"); 
			curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());
			curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
			cout <<"Uploading...\n";
			res = curl_easy_perform(curl);
			if(res != CURLE_OK)
				fprintf(stderr, "Failed to upload to server: %s\n", curl_easy_strerror(res));
			curl_easy_cleanup(curl);
		}
	}

        //params find and replace cannot be NULL
        void findAndReplace( std::string& source, const char* find, const char* replace )
	{
	  size_t findLen = strlen(find);
	  size_t replaceLen = strlen(replace);
	  size_t pos = 0;
	  
	  //search for the next occurrence of find within source
	  while ((pos = source.find( find, pos)) != std::string::npos)
	    {
	      //replace the found string with the replacement
	      source.replace( pos, findLen, replace );
	      
	      //the next line keeps you from searching your replace string, 
	      //so your could replace "hello" with "hello world" 
	      //and not have it blow chunks.
	      pos += replaceLen; 
	    }
	}

	int addJString(std::string &data, const char *name, const char *value, int comma){
	        std::string temp = value;
		findAndReplace(temp, "\\", "\\\\");
		findAndReplace(temp, "\"", "\\\"");
	        data+="\"";
		data+=name;
		data+="\":\"";
		data+=temp.c_str();
		data+="\"";
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
	int i;

	int numEntries=0;
	
	struct eventRec *log;
	FILE *log_fp;
	int lineNum = 0;
	struct bhistReq *reqPtr;
	struct jobFinishLog *jf;
	struct jobNewLog *nj;
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
	char ch;
	if (!url.empty())
	{
		ch=*url.rbegin();
	}	
	if (ch!='/'){
		url+="/";
	}
	url+="cluster/" + clusterName + "/upload";
	log_fp=fopen(logFilePath.c_str(), "r");
	if (log_fp==NULL){
		errx(1,"Unable to open log file: %s", logFilePath.c_str());
	}
	
	jsonData="[\n";


	while(1){
		if (numEntries>=MAX_ENTRIES){
			numEntries=0;
			jsonData+="\n]\n";
			uploadData(jsonData, url);
			jsonData="[\n";
			lineOne=1;
		}
		log = lsb_geteventrec(log_fp, &lineNum);
		if (log == NULL && lsberrno==LSBE_EOF){
			break;
		}
		switch (log->type) {
			case EVENT_JOB_FINISH:
				if (!lineOne){
					jsonData+=",\n";
				}
				lineOne=0;
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
				addJString(jsonData,"error_file", jf->errFile,1);
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
				++numEntries;
				break;
				

			case EVENT_JOB_NEW:
				nj=&(log->eventLog.jobNewLog);
				if (!lineOne){
					jsonData+=",\n";
				}
				lineOne=0;
				jsonData+="{\n";
				addJString(jsonData,"type","job_new",1);
				addJInt(jsonData,"job_id",nj->jobId,1);
				addJInt(jsonData,"user_id",nj->userId,1);
				addJString(jsonData,"user_name",nj->userName,1);
				addJInt(jsonData,"options",nj->options,1);
				addJInt(jsonData,"options2",nj->options2,1);
				addJInt(jsonData,"num_processors",nj->numProcessors,1);
				addJTime(jsonData,"submit_time",nj->submitTime,1);
				addJTime(jsonData,"begin_time",nj->beginTime,1);
				addJTime(jsonData,"term_time",nj->termTime,1);
				addJInt(jsonData,"checkpoint_signal_value",nj->sigValue,1);
				addJInt(jsonData,"checkpoint_period",nj->chkpntPeriod,1);
				addJInt(jsonData,"restart_process_id",nj->restartPid,1);
				addJString(jsonData,"host_specification_hostname",nj->hostSpec,1);
				addJFloat(jsonData,"host_factor",nj->hostFactor,1);
				addJInt(jsonData,"umask",nj->umask,1);
				addJString(jsonData,"queue",nj->queue,1);
				addJString(jsonData,"requested_resources",nj->resReq,1);
				addJString(jsonData,"submit_host",nj->fromHost,1);
				addJString(jsonData,"cwd",nj->cwd,1);
				addJString(jsonData,"checkpoint_dir",nj->chkpntDir,1);
				addJString(jsonData,"input_file",nj->inFile,1);
				addJString(jsonData,"output_file",nj->outFile,1);
				addJString(jsonData,"error_file",nj->errFile,1);
				addJString(jsonData,"input_file_spool",nj->inFileSpool,1);
				addJString(jsonData,"command_spool",nj->commandSpool,1);
				addJString(jsonData,"job_spool_dir",nj->jobSpoolDir,1);
				addJString(jsonData,"home_directory",nj->subHomeDir,1);
				addJString(jsonData,"job_file",nj->jobFile,1);
				jsonData+="\"requested_hosts\":[\n";
				if (nj->numAskedHosts>0){
					for (i=0;i<nj->numAskedHosts;++i){
						if (i>0){
							jsonData+=",\n";
						}
						jsonData+="\"";
						jsonData+=nj->askedHosts[i];
						jsonData+="\"";
					}	
				}
				jsonData+="\n],\n";
				addJString(jsonData,"dependency_conditions",nj->dependCond,1);
				addJString(jsonData,"job_name",nj->jobName,1);
				addJString(jsonData,"command",nj->command,1);
				addJInt(jsonData,"nxf",nj->nxf,1);
				addJString(jsonData,"pre_execution_command",nj->preExecCmd,1);
				addJString(jsonData,"email_user",nj->mailUser,1);
				addJString(jsonData,"project",nj->projectName,1);
				addJInt(jsonData,"nios_port",nj->niosPort,1);
				addJInt(jsonData,"max_num_processors",nj->maxNumProcessors,1);
				addJString(jsonData,"scheduled_host_type",nj->schedHostType,1);
				addJString(jsonData,"login_shell",nj->loginShell,1);
				addJInt(jsonData,"array_index",nj->idx,1);
				addJInt(jsonData,"user_priority",nj->userPriority,0);
				jsonData+="}";
				++numEntries;
				break;
		}
	}
	jsonData+="\n]\n";
	//cout <<jsonData;
	return 0;
}
