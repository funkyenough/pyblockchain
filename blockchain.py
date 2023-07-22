import hashlib
import datetime
import time
import json

INITIAL_BITS = 0x1d777777
MAX_32BIT = 0xffffff


class Block():
    def __init__(self, index, prev_hash, data, timestamp, bits):
        self.index = index
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.elapsed_time = ""
        self.block_hash = ""

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def to_json(self):
        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "stored_data": self.data,
            "timestamp": self.timestamp.strftime("%Y/%m/%D %H:%M:%S"),
            "bits": hex(self.bits)[2:].rjust(8, "0"),
            "nonce": hex(self.nonce)[2:].rjust(8, "0"),
            "elapsed_time": self.elapsed_time,
            "block_hash": self.block_hash
        }

    def calc_blockhash(self):
        blockheader = str(self.index) + str(self.prev_hash) + str(self.data) + \
            str(self.timestamp) + hex(self.bits)[2:] + str(self.nonce)
        h = hashlib.sha256(blockheader.encode()).hexdigest()
        self.block_hash = h
        return h

    def calc_target(self):

        # e.g. bits = 0x12345678
        # right shift 24 means transform the hex value into binary and move all the bits to the right.
        # 24 bits is 3 bytes, so 6 hex digits. The bits that exceed the variable lengths are discarded
        # therefore it looks like 0x00000012(345678) => 0x00000012
        # 0x00000012 = 18 exponent_bytes = 18 - 3 = 5
        exponent_bytes = (self.bits >> 24) - 3

        # Exponent_bits = 15 * 8 = 120
        exponent_bits = exponent_bytes * 8

        # Bitwise AND Operation is again, transforming the hex value into binary, and returns 1 when the digits of respective digits are both 1, else return 0
        # bits = 0x12345678, 32 bits in length. 0xffffff is only 24 bits in length, so it will be left padded by 0.
        # 0x12345678 = 0001 0010 0011 0100 0101 0110 0111 1000
        # 0x00111111 = 0000 0000 1111 1111 1111 1111 1111 1111
        # Bitwise    = 0000 0000 0011 0100 0101 0110 0111 1000 = 0x00345678 = 0x345678
        # From the result we can see that what happend was the initial byte of the self.bits input is removed.
        coefficient = self.bits & 0xffffff

        # right shift will pad 0 to the end, effectivelly lengthening coefficient by 120 bits (15 bytes). Not sure why in this case it is lengthening
        # The result is effectively multiplying the coefficient by 2 ** 120
        return coefficient << exponent_bits

    def check_valid_hash(self):
        # <= is comparison lmao
        # But why does this check whether the hash is valid?
        return int(self.calc_blockhash(), 16) <= self.calc_target()


class Blockchain():
    def __init__(self, initial_bits):
        self.chain = []
        self.initial_bits = initial_bits

    def add_block(self, block):
        self.chain.append(block)

    def getblockinfo(self, index=-1):
        return print(json.dumps(self.chain[index].to_json(), indent=2, sort_keys=True, ensure_ascii=False))

    def mining(self, block):
        start_time = int(time.time() * 1000)
        while True:
            for n in range(MAX_32BIT + 1):
                block.nonce = n
                if block.check_valid_hash():
                    end_time = int(time.time() * 1000)
                    block.elapsed_time = str(
                        (end_time - start_time) / 1000.0) + "秒"
                    self.add_block(block)
                    self.getblockinfo()
                    return
            new_time = datetime.datatime.now()
            if new_time == block.timestamp:
                block.timestamp += datetime.timedelta(seconds=1)

            else:
                block.timestamp = new_time

    def get_retarget_bits(self):
        if len(self.chain) == 0 or len(self.chain) % 5 != 0:
            return -1
        expected_time = 140 * 5

        if len(self.chain) != 5:
            first_block = self.chain[-(1 + 5)]
        else:
            first_block = self.chain[0]
        last_block = self.chain[-1]

        first_time = first_block.timestamp.timestamp()
        last_time = last_block.timestamp.timestamp()

        total_time = last_time - first_time

        target = last_block.calc_target()
        delta = total_time / expected_time
        if delta < 0.25:
            delta = 0.25
        if delta > 4:
            delta = 4

        new_target = int(target * delta)

        exponent_bytes = (last_block.bits >> 24) - 3
        exponent_bits = exponent_bytes * 8
        temp_bits = new_target >> exponent_bits
        if temp_bits != temp_bits & 0xffffff:
            exponent_bytes += 1
            exponent_bits += 8
        elif temp_bits == temp_bits & 0xffff:
            exponent_bytes -= 1
            epxonent_bites -= 8
        return ((exponent_bytes + 3) << 24) | (new_target >> exponent_bits)

    def create_genesis(self):
        genesis_block = Block(0, "0000000000000000000000000000000000000000000000000000000000000000",
                              "ジェネシスブロック", datetime.datetime.now(), self.initial_bits)
        self.mining(genesis_block)

    def add_newblock(self, i):
        last_block = self.chain[-1]
        block = Block(i + 1, last_block.block_hash, "ブロック" +
                      str(i + 1), datetime.datetime.now(), last_block.bits)
        self.mining(block)


if __name__ == "__main__":
    bc = Blockchain(INITIAL_BITS)
    print("ジェネシスブロックを作成中。。。")
    bc.create_genesis()
    for i in range(30):
        print(str(i + 2) + "番目のブロックを作成中。。。")
        bc.add_newblock(i)
