FIR_PATH = $(shell pwd)/TestHarness.DefaultConfig.1609.fir

CXXFLAGS = -O3 -std=c++11
CLANG_FLAGS = -fno-slp-vectorize -fbracket-depth=1024

UNAME_OS := $(shell uname -s)
ifeq ($(UNAME_OS),Darwin)
	CXXFLAGS += $(CLANG_FLAGS)
endif

ifeq ($(ALL_ON),1)
	CXXFLAGS += -DALL_ON
endif

INCLUDES = -Iriscv/include -I../../firrtl-sig

LIBS = -Lriscv/lib -Wl,-rpath,riscv/lib -lfesvr -lpthread

withVCD_TestHarness.h:
	   cd ../../essent; sbt 'run -O3 -withVCD $(FIR_PATH)'

withFST_TestHarness.h:
	   cd ../../essent; sbt 'run -O3 -withFST $(FIR_PATH)'

withVCD_emulator: emulator.cc withVCD_TestHarness.h libfesvr.so 
	        $(CXX) $(CXXFLAGS) $(INCLUDES) emulator.cc -o emulator_vcd $(LIBS)

withFST_emulator: emulator.cc withFST_TestHarness.h libfesvr.so
	        $(CXX) $(CXXFLAGS) $(INCLUDES) emulator.cc -o emulator_fst $(LIBS)

