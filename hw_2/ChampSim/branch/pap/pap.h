#ifndef BRANCH_PAP_H
#define BRANCH_PAP_H

#include <array>
#include "address.h"
#include "modules.h"
#include "msl/fwcounter.h"

class pap : champsim::modules::branch_predictor
{
  static constexpr std::size_t BHT_SIZE = 1024;
  static constexpr std::size_t HISTORY_LENGTH = 10;
  static constexpr std::size_t PHT_SIZE = 1 << HISTORY_LENGTH;
  static constexpr std::size_t BITS = 2;

  std::array<uint64_t, BHT_SIZE> bht;
  std::array<champsim::msl::fwcounter<BITS>, PHT_SIZE> pht;

public:
  using branch_predictor::branch_predictor;

  bool predict_branch(champsim::address ip);
  void last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type);
};

#endif
