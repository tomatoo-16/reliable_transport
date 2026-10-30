import argparse
import socket

from utils import PacketHeader, compute_checksum


def receiver(receiver_ip, receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout."""

import argparse
import socket
import sys

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16


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


def receiver(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiver_ip, receiver_port))

    connected = False
    sender_address = None

    expected = 1
    buffer = {}

    while True:
        packet, address = sock.recvfrom(2048)

        header, data = parse_packet(packet)

        if header is None:
            continue

        if not connected:

            if header.type != START or header.seq_num != 0:
                continue

            connected = True
            sender_address = address
            expected = 1
            buffer = {}

            ack = make_packet(ACK, 1)
            sock.sendto(ack, address)
            continue

        if address != sender_address:
            continue

        if header.type == DATA:

            seq = header.seq_num

            if expected <= seq < expected + window_size:
                if seq not in buffer:
                    buffer[seq] = data

                while expected in buffer:
                    content = buffer.pop(expected)
                    sys.stdout.buffer.write(content)
                    expected += 1

                sys.stdout.buffer.flush()

            # Cumulative ACK
            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

        elif header.type == END:

            if header.seq_num == expected:
                ack = make_packet(ACK, expected + 1)
                sock.sendto(ack, sender_address)
                break

            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

    sock.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    receiver(
        args.receiver_ip,
        args.receiver_port,
        args.window_size
    )


if __name__ == "__main__":
    main()

import argparse
import socket
import sys

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16


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


def receiver(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiver_ip, receiver_port))

    connected = False
    sender_address = None

    expected = 1
    buffer = {}

    while True:
        packet, address = sock.recvfrom(2048)

        header, data = parse_packet(packet)

        if header is None:
            continue

        if not connected:

            if header.type != START or header.seq_num != 0:
                continue

            connected = True
            sender_address = address
            expected = 1
            buffer = {}

            ack = make_packet(ACK, 1)
            sock.sendto(ack, address)
            continue

        if address != sender_address:
            continue

        if header.type == DATA:

            seq = header.seq_num

            if expected <= seq < expected + window_size:
                if seq not in buffer:
                    buffer[seq] = data

                while expected in buffer:
                    content = buffer.pop(expected)
                    sys.stdout.buffer.write(content)
                    expected += 1

                sys.stdout.buffer.flush()

            # Cumulative ACK
            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

        elif header.type == END:

            if header.seq_num == expected:
                ack = make_packet(ACK, expected + 1)
                sock.sendto(ack, sender_address)
                break

            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

    sock.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    receiver(
        args.receiver_ip,
        args.receiver_port,
        args.window_size
    )


if __name__ == "__main__":
    main()

import argparse
import socket
import sys

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16


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


def receiver(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiver_ip, receiver_port))

    connected = False
    sender_address = None

    expected = 1
    buffer = {}

    while True:
        packet, address = sock.recvfrom(2048)

        header, data = parse_packet(packet)

        if header is None:
            continue

        if not connected:

            if header.type != START or header.seq_num != 0:
                continue

            connected = True
            sender_address = address
            expected = 1
            buffer = {}

            ack = make_packet(ACK, 1)
            sock.sendto(ack, address)
            continue

        if address != sender_address:
            continue

        if header.type == DATA:

            seq = header.seq_num

            if expected <= seq < expected + window_size:
                if seq not in buffer:
                    buffer[seq] = data

                while expected in buffer:
                    content = buffer.pop(expected)
                    sys.stdout.buffer.write(content)
                    expected += 1

                sys.stdout.buffer.flush()

            # Cumulative ACK
            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

        elif header.type == END:

            if header.seq_num == expected:
                ack = make_packet(ACK, expected + 1)
                sock.sendto(ack, sender_address)
                break

            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

    sock.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    receiver(
        args.receiver_ip,
        args.receiver_port,
        args.window_size
    )


if __name__ == "__main__":
    main()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((receiver_ip, receiver_port))
    while True:
        # Receive packet; address includes both IP and port
        pkt, address = s.recvfrom(2048)

        # Extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16 : 16 + pkt_header.length]

        # Verity checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
            print("checksums not match")
        print(msg)


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

    receiver(args.receiver_ip, args.receiver_port, args.window_size)


if __name__ == "__main__":
    main()

import argparse
import socket
import sys

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16


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


def receiver(receiver_ip, receiver_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiver_ip, receiver_port))

    connected = False
    sender_address = None

    expected = 1
    buffer = {}

    while True:
        packet, address = sock.recvfrom(2048)

        header, data = parse_packet(packet)

        if header is None:
            continue

        if not connected:

            if header.type != START or header.seq_num != 0:
                continue

            connected = True
            sender_address = address
            expected = 1
            buffer = {}

            ack = make_packet(ACK, 1)
            sock.sendto(ack, address)
            continue

        if address != sender_address:
            continue

        if header.type == DATA:

            seq = header.seq_num

            if expected <= seq < expected + window_size:
                if seq not in buffer:
                    buffer[seq] = data

                while expected in buffer:
                    content = buffer.pop(expected)
                    sys.stdout.buffer.write(content)
                    expected += 1

                sys.stdout.buffer.flush()

            # Cumulative ACK
            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

        elif header.type == END:

            if header.seq_num == expected:
                ack = make_packet(ACK, expected + 1)
                sock.sendto(ack, sender_address)
                break

            ack = make_packet(ACK, expected)
            sock.sendto(ack, sender_address)

    sock.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("receiver_ip")
    parser.add_argument("receiver_port", type=int)
    parser.add_argument("window_size", type=int)

    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("window_size must be positive")

    receiver(
        args.receiver_ip,
        args.receiver_port,
        args.window_size
    )


if __name__ == "__main__":
    main()
