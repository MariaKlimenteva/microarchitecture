#include "gag.h"

bool gag::predict_branch(champsim::address ip)
{
  auto index = global_history & (TABLE_SIZE - 1);
  auto value = pht[index];
  return value.value() >= (value.maximum / 2 + 1);
}

void gag::last_branch_result(champsim::address ip, champsim::address branch_target, bool taken, uint8_t branch_type)
{
  auto index = global_history & (TABLE_SIZE - 1);
  pht[index] += taken ? 1 : -1;
  global_history = ((global_history << 1) | (taken ? 1 : 0)) & (TABLE_SIZE - 1);
}
