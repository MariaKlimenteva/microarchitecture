#include "plru.h"
#include <cmath>
#include <iostream>

plru::plru(CACHE* cache) : plru(cache, cache->NUM_SET, cache->NUM_WAY) {
    std::cout << "PLRU policy initialized!" << std::endl;
}

plru::plru(CACHE* cache, long sets, long ways) : replacement(cache), NUM_WAY(ways), tree_bits(sets * (ways - 1), 0) {}

long plru::find_victim(uint32_t triggering_cpu, uint64_t instr_id, long set, const champsim::cache_block* current_set, champsim::address ip,
                      champsim::address full_addr, access_type type)
{
  long index = 0;
  long offset = set * (NUM_WAY - 1);

  for (uint32_t i = 0; i < (uint32_t)std::log2(NUM_WAY); ++i) {
    if (tree_bits[offset + index] == 0) {
      index = 2 * index + 1;
    } else {
      index = 2 * index + 2;
    }
  }
  return index - (NUM_WAY - 1);
}

void plru::update_replacement_state(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip,
                                   champsim::address victim_addr, access_type type, uint8_t hit)
{
  if (hit) {
    long index = way + (NUM_WAY - 1);
    long offset = set * (NUM_WAY - 1);
    while (index > 0) {
      long parent = (index - 1) / 2;
      if (index % 2 == 1) {
        tree_bits[offset + parent] = 1;
      } else {
        tree_bits[offset + parent] = 0;
      }
      index = parent;
    }
  }
}

void plru::replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                                 access_type type)
{
  update_replacement_state(triggering_cpu, set, way, full_addr, ip, victim_addr, type, 1);
}
