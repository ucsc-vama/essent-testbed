# Run Rocket Chip to get .fir (FIRRTL) file of design
generated_dir = $(abspath riscv-mini/generated-src)
fir_filename = Tile.fir
fir_path = $(abspath $(fir_filename))

Tile.h: $(fir_filename)
	cd ../../essent; sbt 'run -O3 $(fir_path)'

withVCD: $(fir_filename)
	cd ../../essent; sbt 'run -O3 -withVCD $(fir_path)'

withFST: $(fir_filename)
	cd ../../essent; sbt 'run -O3 -withFST $(fir_path)'

CXXFLAGS = -O3 -std=c++11
INCLUDES = -I../../firrtl-sig	

top: top.cc mm.cc mm.h Tile.h
	$(CXX) $(CXXFLAGS) $(INCLUDES) top.cc mm.cc -o top 

top_withVCD: top.cc mm.cc mm.h withVCD
	$(CXX) $(CXXFLAGS) $(INCLUDES) top.cc mm.cc -o top_vcd 

top_withFST: top.cc mm.cc mm.h withFST
	$(CXX) $(CXXFLAGS) $(INCLUDES) top.cc mm.cc -o top_fst 

.PHONY: clean
clean:
	rm -rf $(fir_filename) Tile.h top VTile test-*

VTile: riscv-mini/README.md
	cd riscv-mini; make verilator
	cp riscv-mini/VTile .

.PHONY: test
test: top VTile
	./test.sh
