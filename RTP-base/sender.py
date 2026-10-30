
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
CHUNK_SIZE = 1456
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


def parse_packet(packet):
    if len(packet) < HEADER_SIZE:
        return None, None

    header = PacketHeader(packet[:HEADER_SIZE])
    data = packet[HEADER_SIZE:HEADER_SIZE + header.length]

    if len(data) != header.length:
        return None, None

    checksum = header.checksum
    header.checksum = 0

    if checksum != compute_checksum(header / data):
        return None, None

    return header, data


def sender(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    address = (receiver_ip, receiver_port)

    # START handshake
    start_packet = make_packet(START, 0)

    while True:
        sock.sendto(start_packet, address)

        try:
            response, _ = sock.recvfrom(2048)
            header, _ = parse_packet(response)

            if header and header.type == ACK and header.seq_num == 1:
                break
        except socket.timeout:
            continue

    # Read input and split into chunks
    message = sys.stdin.buffer.read()

    chunks = [
        message[i:i + CHUNK_SIZE]
        for i in range(0, len(message), CHUNK_SIZE)
    ]

    packets = {
        i + 1: make_packet(DATA, i + 1, chunk)
        for i, chunk in enumerate(chunks)
    }

    base = 1
    next_seq = 1
    total = len(chunks)
    timer = None

    # Sliding window
    while base <= total:

        while next_seq <= total and next_seq < base + window_size:
            sock.sendto(packets[next_seq], address)

            if timer is None:
                timer = time.monotonic()

            next_seq += 1

        try:
            response, _ = sock.recvfrom(2048)
            header, _ = parse_packet(response)

            if header is None or header.type != ACK:
                continue

            ack = header.seq_num

            if base < ack <= next_seq:
                base = ack

                if base == next_seq:
                    timer = None
                else:
                    timer = time.monotonic()

        except socket.timeout:
            if timer is not None:
                if time.monotonic() - timer >= TIMEOUT:
                    for seq in range(base, next_seq):
                        sock.sendto(packets[seq], address)

                    timer = time.monotonic()

    # END packet
    end_seq = total + 1
    end_packet = make_packet(END, end_seq)

    while True:
        sock.sendto(end_packet, address)
        end_time = time.monotonic()

        while time.monotonic() - end_time < TIMEOUT:
            try:
                response, _ = sock.recvfrom(2048)
                header, _ = parse_packet(response)

                if (header and header.type == ACK
                        and header.seq_num == end_seq + 1):
                    sock.close()
                    return

            except socket.timeout:
                break

        # END ACK may be lost; stop after 500 ms
        sock.close()
        return


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    sender(
        args.receiver_ip,
        args.receiver_port,
        args.window_size
    )


if __name__ == "__main__":
    main()
import argparse
import socket

from utils import PacketHeader, compute_checksum


def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pkt_header = PacketHeader(type=2, seq_num=10, length=14)
    pkt_header.checksum = compute_checksum(pkt_header / "Hello, world!\n")
    pkt = pkt_header / "Hello, world!\n"
    s.sendto(bytes(pkt), (receiver_ip, receiver_port))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "receiver_ip", help="The IP address of the host that receiver is running on"
    )
    parser.add_argument(
        "receiver_port", type=int, help="The port number on which receiver is listening"
    )
    parser.add_argument(
        "window_size", type=int, help="Maximum number of outstanding packets"
    )
    args = parser.parse_args()

    sender(args.receiver_ip, args.receiver_port, args.window_size)


if __name__ == "__main__":
    main()
