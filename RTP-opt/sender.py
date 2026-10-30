import argparse
import socket
import sys
import time

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16
MAX_PACKET_SIZE = 1472
CHUNK_SIZE = MAX_PACKET_SIZE - HEADER_SIZE

TIMEOUT = 0.5


def make_packet(packet_type, seq_num, data=b""):
    header = PacketHeader(
        type=packet_type,
        seq_num=seq_num,
        length=len(data),
        checksum=0
    )
    packet = header / data
    header.checksum = compute_checksum(packet)
    return bytes(header / data)


def parse_packet(raw):
    if len(raw) < HEADER_SIZE:
        return None
    header = PacketHeader(raw[:HEADER_SIZE])
    if len(raw) != HEADER_SIZE + header.length:
        return None
    data = raw[HEADER_SIZE:]
    received_checksum = header.checksum
    header.checksum = 0
    calculated_checksum = compute_checksum(header / data)
    if received_checksum != calculated_checksum:
        return None
    return header


def sender(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.05)
    address = (receiver_ip, receiver_port)

    # STEP 1: Handshake
    start_packet = make_packet(START, 0)
    while True:
        sock.sendto(start_packet, address)
        try:
            raw, _ = sock.recvfrom(MAX_PACKET_SIZE)
            header = parse_packet(raw)
            if header is not None and header.type == ACK and header.seq_num == 1:
                break
        except socket.timeout:
            continue

    print("START acknowledged", file=sys.stderr)

    # STEP 2: Read Data
    message = sys.stdin.buffer.read()
    chunks = [
        message[i:i + CHUNK_SIZE]
        for i in range(0, len(message), CHUNK_SIZE)
    ]
    total = len(chunks)
    packets = {}
    for i, chunk in enumerate(chunks):
        seq = i + 1
        packets[seq] = make_packet(DATA, seq, chunk)

    print("Total DATA packets:", total, file=sys.stderr)

    # STEP 3: Sliding Window
    base = 1
    next_seq = 1
    acknowledged = set()
    timer = None

    while base <= total:
        # Send packets in window
        while next_seq <= total and next_seq < base + window_size:
            sock.sendto(packets[next_seq], address)
            print("Send DATA:", next_seq, file=sys.stderr)
            if timer is None:
                timer = time.monotonic()
            next_seq += 1

        # Receive ACKs
        try:
            raw, _ = sock.recvfrom(MAX_PACKET_SIZE)
            header = parse_packet(raw)
            if header is not None and header.type == ACK:
                ack = header.seq_num
                if base <= ack < next_seq:
                    if ack not in acknowledged:
                        acknowledged.add(ack)
                        print("Received ACK:", ack, file=sys.stderr)

                    old_base = base
                    while base in acknowledged:
                        acknowledged.remove(base)
                        base += 1

                    if base > old_base:
                        if base < next_seq:
                            timer = time.monotonic()
                        else:
                            timer = None
        except socket.timeout:
            pass

        # Timeout / Retransmission
        if base <= total and timer is not None:
            if time.monotonic() - timer >= TIMEOUT:
                print("TIMEOUT: retransmitting unACKed packets", file=sys.stderr)
                for seq in range(base, next_seq):
                    if seq not in acknowledged:
                        print("Retransmit DATA:", seq, file=sys.stderr)
                        sock.sendto(packets[seq], address)
                timer = time.monotonic()

    # STEP 4: Send END
    end_seq = total + 1
    end_packet = make_packet(END, end_seq)
    print("Send END:", end_seq, file=sys.stderr)

    while True:
        sock.sendto(end_packet, address)
        try:
            raw, _ = sock.recvfrom(MAX_PACKET_SIZE)
            header = parse_packet(raw)
            if header is not None and header.type == ACK and header.seq_num == end_seq + 1:
                print("END acknowledged", file=sys.stderr)
                break
        except socket.timeout:
            continue

    sock.close()
    print("Sender finished", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)
    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    sender(args.receiver_ip, args.receiver_port, args.window_size)


if __name__ == "__main__":
    main()
