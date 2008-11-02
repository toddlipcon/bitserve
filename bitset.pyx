ctypedef int size_t
cdef extern from "stdlib.h":
  void *malloc(size_t size)
  void *calloc(size_t nmemb, size_t size)
  void *realloc(void *ptr, size_t size)
  void *memcpy(void *dest, void *src, size_t n)
  int free(void*)
  int sizeof()

cdef extern from "strings.h":
  void bzero(void *s, size_t n)
  
cdef class BitSet:

  cdef unsigned char *data
  cdef size_t dlen, bitlen
  
  def __new__(self, initial_bit_len=0):
    cdef size_t initial_len
    initial_len = initial_bit_len / 8
    if initial_bit_len % 8 > 0:
      initial_len = initial_len + 1
      
    if initial_len > 0:
      self.data = <unsigned char *>calloc(initial_len, 1)
    else:
      self.data = NULL
    self.dlen = initial_len
    self.bitlen = initial_bit_len
    
  def __dealloc__(self):
    if self.data != NULL:
      free(self.data)

  def __str__(self):
    cdef char *out
    out = <char *>malloc(self.bitlen + 1)

    cdef i
    for 0 <= i < self.bitlen:
      if self.__getitem__(i):
        out[i] = c'1'
      else:
        out[i] = c'0'

    out[self.bitlen] = c'\0'
    return out

  def __len__(self):
    return self.bitlen

  def __setitem__(self, int bit, int val):
    cdef size_t byte, bit_in_byte, need_len

    byte = bit / 8
    bit_in_byte = bit % 8

    need_len = byte + 1
    if self.dlen < need_len:
      print "realloc (have %d need %d)" % (self.dlen, need_len)
      self.data = <unsigned char *>realloc(self.data, need_len)
      if self.data == NULL:
        raise "out of memory"
      bzero(self.data + self.dlen,
            need_len - self.dlen)
      self.dlen = need_len

    if bit >= self.bitlen:
      self.bitlen = bit + 1

    cdef unsigned char bitmask
    bitmask = (val << bit_in_byte)
    self.data[byte] = self.data[byte] & (~bitmask) | bitmask


  def __iadd__(self, int val):
    cdef int bit
    bit = self.bitlen
    self.__setitem__(bit, val)
    return self

  def __getitem__(self, int bit):
    cdef size_t byte, bit_in_byte
    byte = bit / 8
    bit_in_byte = bit % 8
    
    if self.dlen <= byte:
      return 0

    return self.data[byte] & (1 << bit_in_byte)

  def __or__(BitSet self, BitSet other):
    cdef size_t minlen, maxlen
    cdef BitSet bigger

    if self.dlen < other.dlen:
      minlen = self.dlen
      maxlen = other.dlen
      bigger = other
    else:
      minlen = other.dlen
      maxlen = self.dlen
      bigger = self
      
    cdef BitSet result
    result = BitSet(maxlen * 8)

    cdef size_t i

    # First copy as much as possible using
    # machine word size
    cdef unsigned int *a_int, *b_int, *r_int
    a_int = <unsigned int *>self.data
    b_int = <unsigned int *>other.data
    r_int = <unsigned int *>result.data

    cdef int minlen_words
    minlen_words = minlen / sizeof(int)

    i = 0
    while i < minlen_words:
      r_int[i] = a_int[i] | b_int[i]
      i = i + 1

    # now we're going to use i in terms of bytes, so
    # the counter needs to be turned into a byte counter
    i = i * sizeof(int)

    while i < minlen:
      result.data[i] = self.data[i] | other.data[i]
      i = i + 1

    # now we can just use memcpy to copy the rest
    # since we're orring with 0s on the smaller side
    cdef unsigned char *src, *dst
    dst = result.data + i
    src = bigger.data + i
    memcpy(<void *>dst, <void *>src, maxlen - minlen)
    
    return result


  def __and__(BitSet self, BitSet other):
    cdef size_t minlen, maxlen, maxbitlen

    if self.dlen < other.dlen:
      minlen = self.dlen
      maxlen = other.dlen
      maxbitlen = other.bitlen
    else:
      minlen = other.dlen
      maxlen = self.dlen
      maxbitlen = self.bitlen
      
    cdef BitSet result
    result = BitSet(maxbitlen)

    cdef size_t i

    # First copy as much as possible using
    # machine word size
    cdef unsigned int *a_int, *b_int, *r_int
    a_int = <unsigned int *>self.data
    b_int = <unsigned int *>other.data
    r_int = <unsigned int *>result.data

    cdef int minlen_words
    minlen_words = minlen / sizeof(int)

    i = 0
    while i < minlen_words:
      r_int[i] = a_int[i] & b_int[i]
      i = i + 1

    # now we're going to use i in terms of bytes, so
    # the counter needs to be turned into a byte counter
    i = i * sizeof(int)

    while i < minlen:
      result.data[i] = self.data[i] & other.data[i]
      i = i + 1

    # the rest of the bitset is just zeros
    return result
