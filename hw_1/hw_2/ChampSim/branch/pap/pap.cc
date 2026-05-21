#include "pap.h"

bool pap::predict_branch(champsim::address ip)
{
  auto bht_index = (ip.to<uint64_t>() >> 2) & (BHT_SIZE - 1);
  auto history = bht[bht_index];
  auto pht_index = history & (PHT_SIZE - 1);
  
  auto value = pht[pht_index];
  return value.value() >= (value.maximum / 2 + 1);
}

void pap::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type)
{
  auto bht_index = (ip.to<uint64_t>() >> 2) & (BHT_SIZE - 1);
  auto history = bht[bht_index];
  auto pht_index = history & (PHT_SIZE - 1);

  pht[pht_index] += taken ? 1 : -1;
  bht[bht_index] = ((history << 1) | (taken ? 1 : 0)) & (PHT_SIZE - 1);
}
