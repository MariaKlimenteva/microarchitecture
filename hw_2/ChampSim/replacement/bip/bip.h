#ifndef BIP_H
#define BIP_H

#include "../lru/lru.h"
#include <cstdlib>

class bip : public lru
{
public:
  explicit bip(CACHE* cache);
  void replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                              access_type type);
};

#endif
