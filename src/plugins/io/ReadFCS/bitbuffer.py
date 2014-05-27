class BitBuffer:
    def __init__(self, buf=''):
        self.buf=[ord(x) for x in buf]

        self.pos=0
        self.len=len(buf)*8

        self.closed = False
        self.softspace = 0

    def close(self):
        """Let me think... Closes and flushes the toilet!"""
        if not self.closed:
            self.closed = True
            del self.buf, self.pos, self.len, self.softspace

    def isatty(self):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return 0

    def seek(self, pos, mode = 0):
        """Set new position"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if mode == 1:
            pos += self.pos
        elif mode == 2:
            pos += self.len
        self.pos = max(0, pos)

    def tell(self):
        """Tell current position"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        return self.pos

    def flush(self):
        """Flush the toilet"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"

    def truncate(self, size=None):
        if self.closed:
            raise ValueError, "I/O operation on closed file"
        if size is None:
            size = self.pos
        elif size < 0:
            raise IOError(EINVAL, "Negative size not allowed")
        elif size < self.pos:
            self.pos = size

        self.len=size
        self.buf = self.buf[:(size//8)+(size%8 != 0)]
        if self.buf!=[]: self.buf[-1]=self.buf[-1] & (1<<(size%8))-1
        
    def writebits(self, n, bitlen):
        """Writes bits"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"

        n &= (1L << bitlen)-1

        newpos = self.pos + bitlen

        startBPos=self.pos%8
        startBlock=self.pos//8

        endBPos=newpos%8
        endBlock=newpos//8+(endBPos != 0)

        #print startBlock, startBPos, endBlock, endBPos

        while len(self.buf) < endBlock: self.buf += [0]

        pos=startBPos

        while bitlen > 0:
            bitsLeft=8-(pos%8)
            if bitsLeft > bitlen: bitsLeft=bitlen
            
            mask=(1<<bitsLeft)-1

            self.buf[startBlock+(pos//8)] ^= self.buf[startBlock+(pos//8)]&(mask<<(pos%8))
            self.buf[startBlock+(pos//8)] |= int(n&mask)<<(pos%8)
        
            n >>= bitsLeft
            bitlen -= bitsLeft
            
            pos+=bitsLeft

        self.pos = newpos
        if self.pos > self.len:
            self.len=self.pos

    def readbits(self, bitlen):
        """Reads bits"""
        
        if self.closed:
            raise ValueError, "I/O operation on closed file"

        newpos = self.pos + bitlen

        startBPos=self.pos%8
        startBlock=self.pos//8

        endBPos=newpos%8
        endBlock=newpos//8+(endBPos != 0)

        ret=0

        pos=startBPos
        shift=0

        while bitlen > 0:
            bitsLeft=8-(pos%8)
            if bitsLeft > bitlen: bitsLeft=bitlen

            mask=(1<<bitsLeft)-1

            ret |= long((self.buf[startBlock+(pos//8)] >> (pos%8)) & mask) << shift

            shift += bitsLeft

            bitlen -= bitsLeft
            pos+=bitsLeft

        self.pos = newpos
        return ret

    def getvalue(self):
        """Get the buffer"""
        
        return ''.join(map(chr, self.buf))

    def write(self, s):
        for c in str(s):
            self.writebits(ord(c), 8)

    def writelines(self, list):
        self.write(''.join(list))

    def read(self, i):
        ret=[]
        for i in range(i):
            ret.append( chr(self.readbits(8)) )

        return ''.join(ret)

    def writebit(self, b):
        """Writes Bit (1bit)"""
        
        self.writebits(b, 1)

    def readbit(self):
        """Reads Bit (1bit)"""
        
        return self.readbits(1)

    def writebyte(self, i):
        """Writes Byte (8bits)"""
        
        self.writebits(i, 8)

    def readbyte(self):
        """Reads Byte (8bits)"""
        
        return self.readbits(8)

    def writeword(self, i):
        """Writes Word (16bits)"""
        
        self.writebits(i, 16)

    def readword(self):
        """Reads Word (16bits)"""
        
        return self.readbits(16)

    def writedword(self, i):
        """Writes DWord (32bits)"""
        
        self.writebits(i, 32)

    def readdword(self):
        """Reads DWord (32bits)"""
        
        return self.readbits(32)

    def writevbl(self, n):
        """Writes Variable bit length."""
        
        self.writebit(n < 0)
        n=abs(n)
        self.writebits(n, 6)
        n >>= 6

        while n:
            self.writebit(1)
            self.writebits(n, 8 )
            n >>= 8
        
        self.writebit(0)

    def readvbl(self):
        """Reads Variable bit length."""
        
        isNeg=self.readbit()
        r=self.readbits(6)
        pos=6

        while self.readbit():
            r |= self.readbits(8) << pos
            pos+=8

        if isNeg: r=-r

        return r

if __name__=='__main__':
    bb=BitBuffer('hauki on iso kala')

    bb.writebits(1, 1)
    bb.writebits(0, 1)
    bb.writebits(1, 1)

    bb.seek(0)
    #bb.truncate()

    print bb.readbit()
    print bb.readbit()
    print bb.readbit()

    print `bb.getvalue()`
