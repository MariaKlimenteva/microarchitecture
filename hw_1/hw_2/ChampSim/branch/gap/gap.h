#ifndef BRANCH_GAP_H
#define BRANCH_GAP_H

#include <array>
#include "address.h"
#include "modules.h"
#include "msl/fwcounter.h"

class gap : champsim::modules::branch_predictor
{
  static constexpr std::size_t HISTORY_LENGTH = 10;
  static constexpr std::size_t TABLE_SIZE = 1 << 14;
  static constexpr std::size_t BITS = 2;

  uint64_t global_history = 0;
  std::array<champsim::msl::fwcounter<BITS>, TABLE_SIZE> pht;

public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);
};

#endif
