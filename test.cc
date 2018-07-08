#include <string.h>

int test(int a, int b)
{
  a += 2;
  while (a >20) 
  a/=6;
  a/=4;
  return a + b * 2;
}

void square(void* dst, void* src)
{
  memcpy(dst, src, 11112);
}
