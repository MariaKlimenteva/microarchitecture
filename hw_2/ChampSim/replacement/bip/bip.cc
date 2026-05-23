#include "bip.h"

bip::bip(CACHE* cache) : lru(cache) {}

void bip::replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                 access_type type)
{
  if ((std::rand() % 32) == 0) {
    last_used_cycles.at((std::size_t)(set * NUM_WAY + way)) = cycle++;
  } else {
    last_used_cycles.at((std::size_t)(set * NUM_WAY + way)) = 0;
  }
}
