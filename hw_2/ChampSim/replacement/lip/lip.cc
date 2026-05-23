#include "lip.h"

lip::lip(CACHE* cache) : lru(cache) {}

void lip::replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                 access_type type)
{
  last_used_cycles.at((std::size_t)(set * NUM_WAY + way)) = 0;
}
