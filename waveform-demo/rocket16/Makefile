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

riscv_dir := $(shell pwd)/riscv

riscv/lib/libfesvr.so:
	git submodule update --init riscv-fesvr
	cd riscv-fesvr; git checkout `cat ../fesvr.commit`
	patch riscv-fesvr/fesvr/dtm.cc ../riscv-fesvr.patch
	mkdir $(riscv_dir)
	cd riscv-fesvr; mkdir build; cd build; ../configure --prefix=$(riscv_dir) --target=riscv64-unknown-elf; make install

withVCD_TestHarness.h:
	   cd ../../essent; sbt 'run -O3 -withVCD $(FIR_PATH)'

withFST_TestHarness.h:
	   cd ../../essent; sbt 'run -O3 -withFST $(FIR_PATH)'

withVCD_emulator: emulator.cc withVCD_TestHarness.h riscv/lib/libfesvr.so 
	        $(CXX) $(CXXFLAGS) $(INCLUDES) emulator.cc -o emulator_vcd $(LIBS)

withFST_emulator: emulator.cc withFST_TestHarness.h riscv/lib/libfesvr.so
	        $(CXX) $(CXXFLAGS) $(INCLUDES) emulator.cc -o emulator_fst $(LIBS)

