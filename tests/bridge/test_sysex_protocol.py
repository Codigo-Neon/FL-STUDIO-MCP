"""Tests for SysEx bridge protocol."""
import pytest
from bridge.sysex_protocol import (
    MAGIC, MFG_ID, MAX_PAYLOAD,
    pack_message, unpack_packet,
    SysExProtocolError,
)


class TestPackMessage:
    def test_small_message_one_chunk(self):
        chunks = pack_message(seq=1, payload=b'{"x":1}')
        assert len(chunks) == 1
        assert chunks[0][0] == 0xF0  # start
        assert chunks[0][-1] == 0xF7  # end
        assert chunks[0][1] == MFG_ID
        assert chunks[0][2:4] == MAGIC

    def test_seq_encoded_two_bytes_7bit(self):
        chunks = pack_message(seq=0x3FFF, payload=b'x')  # 16383, max value
        # SEQ_HI at index 4, SEQ_LO at index 5
        assert chunks[0][4] == 0x7F
        assert chunks[0][5] == 0x7F

    def test_seq_zero(self):
        chunks = pack_message(seq=0, payload=b'x')
        assert chunks[0][4] == 0x00
        assert chunks[0][5] == 0x00

    def test_seq_overflow_rejected(self):
        with pytest.raises(SysExProtocolError, match="seq"):
            pack_message(seq=0x4000, payload=b'x')

    def test_seq_negative_rejected(self):
        with pytest.raises(SysExProtocolError, match="seq"):
            pack_message(seq=-1, payload=b'x')

    def test_empty_payload_produces_single_chunk(self):
        chunks = pack_message(seq=1, payload=b'')
        assert len(chunks) == 1
        # CHUNK_IDX=0, CHUNK_CNT=1
        assert chunks[0][6] == 0
        assert chunks[0][7] == 1
        # Empty body: bytes between header end (8) and F7 should be empty
        assert chunks[0][8:-1] == b''

    def test_chunk_index_and_count_for_single(self):
        chunks = pack_message(seq=5, payload=b'x')
        # CHUNK_IDX at 6, CHUNK_CNT at 7
        assert chunks[0][6] == 0
        assert chunks[0][7] == 1

    def test_payload_inside_packet(self):
        chunks = pack_message(seq=1, payload=b'{"x":1}')
        # payload starts at index 8, F7 at last
        assert bytes(chunks[0][8:-1]) == b'{"x":1}'

    def test_non_ascii_payload_rejected(self):
        # SysEx data bytes must be 0-127
        with pytest.raises(SysExProtocolError, match="ASCII"):
            pack_message(seq=1, payload=b'\x80\x81')


class TestUnpackPacket:
    def test_unpack_single_chunk(self):
        chunks = pack_message(seq=42, payload=b'{"x":1}')
        result = unpack_packet(chunks[0])
        assert result.seq == 42
        assert result.chunk_idx == 0
        assert result.chunk_cnt == 1
        assert result.payload == b'{"x":1}'

    def test_unpack_rejects_non_sysex(self):
        with pytest.raises(SysExProtocolError, match="F0"):
            unpack_packet(b'\x90\x3c\x64')  # MIDI note on

    def test_unpack_rejects_other_manufacturer(self):
        bad = bytes([0xF0, 0x41, 0x00, 0x01, 0, 0, 0, 1, ord('x'), 0xF7])
        with pytest.raises(SysExProtocolError, match="manufacturer"):
            unpack_packet(bad)

    def test_unpack_rejects_bad_magic(self):
        bad = bytes([0xF0, 0x7D, 0x7F, 0x7E, 0, 0, 0, 1, ord('x'), 0xF7])
        with pytest.raises(SysExProtocolError, match="magic"):
            unpack_packet(bad)

    def test_unpack_rejects_truncated(self):
        with pytest.raises(SysExProtocolError, match="too short"):
            unpack_packet(b'\xF0\x7D\x00\x01\xF7')

    def test_unpack_rejects_missing_F7(self):
        # All header present but no F7 terminator
        bad = bytes([0xF0, 0x7D]) + MAGIC + bytes([0, 0, 0, 1, ord('x')])
        with pytest.raises(SysExProtocolError, match="F7"):
            unpack_packet(bad)

    def test_unpack_max_seq(self):
        chunks = pack_message(seq=0x3FFF, payload=b'x')
        result = unpack_packet(chunks[0])
        assert result.seq == 0x3FFF


class TestMultiChunk:
    def test_payload_exactly_MAX_PAYLOAD_is_one_chunk(self):
        chunks = pack_message(seq=1, payload=b'x' * MAX_PAYLOAD)
        assert len(chunks) == 1

    def test_payload_one_byte_over_splits(self):
        chunks = pack_message(seq=1, payload=b'x' * (MAX_PAYLOAD + 1))
        assert len(chunks) == 2

    def test_chunk_indices_and_count(self):
        big = b'a' * (MAX_PAYLOAD * 3 - 5)
        chunks = pack_message(seq=2, payload=big)
        assert len(chunks) == 3
        parsed = [unpack_packet(c) for c in chunks]
        assert [p.chunk_idx for p in parsed] == [0, 1, 2]
        assert all(p.chunk_cnt == 3 for p in parsed)


class TestReassembler:
    def test_single_chunk_returns_immediately(self):
        from bridge.sysex_protocol import Reassembler
        chunks = pack_message(seq=10, payload=b'{"hello":1}')
        r = Reassembler()
        result = r.feed(unpack_packet(chunks[0]))
        assert result == b'{"hello":1}'

    def test_multi_chunk_returns_none_until_last(self):
        from bridge.sysex_protocol import Reassembler
        big = b'a' * (MAX_PAYLOAD + 50)
        chunks = pack_message(seq=11, payload=big)
        r = Reassembler()
        assert r.feed(unpack_packet(chunks[0])) is None
        result = r.feed(unpack_packet(chunks[1]))
        assert result == big

    def test_concurrent_sequences_isolated(self):
        from bridge.sysex_protocol import Reassembler
        m1 = pack_message(seq=20, payload=b'a' * (MAX_PAYLOAD + 10))
        m2 = pack_message(seq=21, payload=b'b' * (MAX_PAYLOAD + 10))
        r = Reassembler()
        assert r.feed(unpack_packet(m1[0])) is None
        assert r.feed(unpack_packet(m2[0])) is None
        r1 = r.feed(unpack_packet(m1[1]))
        r2 = r.feed(unpack_packet(m2[1]))
        assert r1 == b'a' * (MAX_PAYLOAD + 10)
        assert r2 == b'b' * (MAX_PAYLOAD + 10)

    def test_out_of_order_chunks(self):
        from bridge.sysex_protocol import Reassembler
        chunks = pack_message(seq=30, payload=b'a' * (MAX_PAYLOAD + 5))
        r = Reassembler()
        # Feed chunk 1 before chunk 0
        assert r.feed(unpack_packet(chunks[1])) is None
        result = r.feed(unpack_packet(chunks[0]))
        assert result == b'a' * (MAX_PAYLOAD + 5)


class TestDictEncoding:
    def test_encode_dict_roundtrip(self):
        from bridge.sysex_protocol import encode_dict, decode_payload
        msg = {"type": "req", "id": "abc", "method": "ping", "params": {}}
        packets = encode_dict(seq=1, message=msg)
        assert len(packets) == 1
        unpacked = unpack_packet(packets[0])
        decoded = decode_payload(unpacked.payload)
        assert decoded == msg

    def test_encode_handles_non_ascii_via_unicode_escape(self):
        from bridge.sysex_protocol import encode_dict, decode_payload
        msg = {"name": "Café", "emoji": "🎵"}
        packets = encode_dict(seq=2, message=msg)
        decoded = decode_payload(unpack_packet(packets[0]).payload)
        assert decoded == msg

    def test_decode_invalid_json(self):
        from bridge.sysex_protocol import decode_payload
        with pytest.raises(SysExProtocolError, match="json"):
            decode_payload(b'not json')
