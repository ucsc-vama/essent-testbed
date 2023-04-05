#include <fesvr/dtm.h>
#include <iostream>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "TestHarness.h"

dtm_t* dtm;
static uint64_t trace_count = 0;

void handle_sigterm(int sig) {
  dtm->stop();
}

void tick_dtm(TestHarness *tile, bool done_reset) {
  // PRINT_SIG(tile->SimDTM_1.debug_req_ready);
  // PRINT_SIG(tile->SimDTM_1.debug_resp_valid);
  // PRINT_SIG(tile->SimDTM_1.debug_resp_bits_resp);
  // PRINT_SIG(tile->SimDTM_1.debug_resp_bits_data);
  if (done_reset) {
    dtm_t::resp resp_bits;
    resp_bits.resp = tile->SimDTM_1.debug_resp_bits_resp.as_single_word();
    resp_bits.data = tile->SimDTM_1.debug_resp_bits_data.as_single_word();

    dtm->tick(tile->SimDTM_1.debug_req_ready.as_single_word(),
              tile->SimDTM_1.debug_resp_valid.as_single_word(),
              resp_bits);

    tile->SimDTM_1.debug_resp_ready = UInt<1>(dtm->resp_ready());
    tile->SimDTM_1.debug_req_valid = UInt<1>(dtm->req_valid());
    tile->SimDTM_1.debug_req_bits_addr = UInt<5>(dtm->req_bits().addr);
    tile->SimDTM_1.debug_req_bits_op = UInt<2>(dtm->req_bits().op);
    tile->SimDTM_1.debug_req_bits_data = UInt<34>(dtm->req_bits().data);

    tile->SimDTM_1.exit = UInt<32>(dtm->done() ? (dtm->exit_code() << 1 | 1) : 0);
  } else {
    tile->SimDTM_1.debug_req_valid = UInt<1>(0);
    tile->SimDTM_1.debug_resp_ready = UInt<1>(0);
    tile->SimDTM_1.exit = UInt<32>(0);
  }
  // PRINT_SIG(tile->SimDTM_1.debug_req_valid);
  // PRINT_SIG(tile->SimDTM_1.debug_req_bits_addr);
  // PRINT_SIG(tile->SimDTM_1.debug_req_bits_op);
  // PRINT_SIG(tile->SimDTM_1.debug_req_bits_data);
  // PRINT_SIG(tile->SimDTM_1.debug_resp_ready);
}

int main(int argc, char** argv) {
  unsigned random_seed = (unsigned)time(NULL) ^ (unsigned)getpid();
  uint64_t max_cycles = -1;
  uint64_t start = 0;
  int ret = 0;
  bool print_cycles = false;
  bool verbose = false;
  bool done_reset = false;

  for (int i = 1; i < argc; i++) {
    std::string arg = argv[i];
    if (arg.substr(0, 2) == "-s")
      random_seed = atoi(argv[i]+2);
    else if (arg == "+verbose")
      verbose = true;
    else if (arg.substr(0, 12) == "+max-cycles=")
      max_cycles = atoll(argv[i]+12);
    else if (arg.substr(0, 7) == "+start=")
      start = atoll(argv[i]+7);
    else if (arg.substr(0, 12) == "+cycle-count")
      print_cycles = true;
  }

  srand(random_seed);
  srand48(random_seed);

  TestHarness *tile = new TestHarness;

  dtm = new dtm_t(std::vector<std::string>(argv + 1, argv + argc));

  signal(SIGTERM, handle_sigterm);
  tile->genWaveHeader();
  tile->reset = UInt<1>(1);
  tick_dtm(tile, done_reset);
  tile->eval(false, verbose, done_reset);
  // reset for several cycles to handle pipelined reset
  for (int i = 0; i < 10; i++) {
    tile->eval(true, verbose, done_reset);
    tick_dtm(tile, done_reset);
  }
  tile->reset = UInt<1>(0);
  tile->eval(false, verbose, done_reset);
  tick_dtm(tile, done_reset);
  done_reset = true;

  while (!dtm->done() && !tile->io_success && trace_count < max_cycles) {
    tile->eval(true, verbose, done_reset);
    tick_dtm(tile, done_reset);
    trace_count++;
  }

  if (dtm->exit_code()) {
    fprintf(stderr, "*** FAILED *** (code = %d, seed %d) after %" PRIu64 " cycles\n", dtm->exit_code(), random_seed, trace_count);
    ret = dtm->exit_code();
  } else if (trace_count == max_cycles) {
    fprintf(stderr, "*** FAILED *** (timeout, seed %d) after %" PRIu64 " cycles\n", random_seed, trace_count);
    ret = 2;
  } else if (verbose || print_cycles) {
    fprintf(stderr, "Completed after %" PRIu64 " cycles\n", trace_count);
  }

  delete tile;
  delete dtm;

  return ret;
}
