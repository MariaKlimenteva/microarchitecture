#ifndef LIP_H
#define LIP_H

#include "../lru/lru.h"

class lip : public lru
{
public:
  explicit lip(CACHE* cache);
  void replacement_cache_fill(uint32_t triggering_cpu, long set, long way, champsim::address full_addr, champsim::address ip, champsim::address victim_addr,
                              access_type type);
};

#endif
