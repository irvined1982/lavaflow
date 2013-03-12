find_path(LSF_INCLUDE_DIR
 lsbatch.h
  paths
	${LSF_DIR}/include
	$ENV{LSF_DIR}/include
	/usr/include
	/usr/local/include
	/opt/local/include
	/opt/openlava/include
	/opt/openlava-2.0/include
)

find_library(LSBATCH_LIB
  liblsbatch.a
  paths
  	${LSF_DIR}/lib
	$ENV{LSF_DIR}/lib
	/usr/lib
	/usr/local/lib
	/opt/local/lib
	/opt/openlava/lib
	/opt/openlava-2.0/lib
)


find_library(LSF_LIB
	liblsf.a
	paths
		${LSF_DIR}/lib
		$ENV{LSF_DIR}/lib
		/usr/lib
		/usr/local/lib
		/opt/local/lib
		/opt/openlava/lib
		/opt/openlava-2.0/lib
)

if (LSF_INCLUDE_DIR AND  LSF_LIB)
	set(LAVA_FOUND "Yes")
  mark_as_advanced(LSF_INCLUDE_DIR)
  mark_as_advanced(LSBATCH_LIB)
  mark_as_advanced(LSF_LIB)
endif(LSF_INCLUDE_DIR AND LSF_LIB)

