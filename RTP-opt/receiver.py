import argparse
import socket
import sys

from utils import PacketHeader, compute_checksum

START = 0
END = 1
DATA = 2
ACK = 3

HEADER_SIZE = 16
MAX_PACKET_SIZE = 1472


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


def receiver(listen_ip, listen_port, window_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))

    # Handshake
    sender_address = None
    while True:
        raw, addr = sock.recvfrom(MAX_PACKET_SIZE)
        header = parse_packet(raw)

        if header is not None and header.type == START:
            sender_address = addr
            ack_packet = make_packet(ACK, 1)
            sock.sendto(ack_packet, sender_address)
            break

    base = 1
    received_buffer = {}

    while True:
        raw, addr = sock.recvfrom(MAX_PACKET_SIZE)
        header = parse_packet(raw)

        if header is None:
            continue

        if header.type == DATA:
            seq = header.seq_num

            # Send ACK for received packet (in window or already received)
            if base <= seq < base + window_size or seq < base:
                ack_packet = make_packet(ACK, seq)
                sock.sendto(ack_packet, sender_address)

            # Store and buffer
            if base <= seq < base + window_size:
                data = raw[HEADER_SIZE:]
                received_buffer[seq] = data

                while base in received_buffer:
                    sys.stdout.buffer.write(received_buffer[base])
                    sys.stdout.buffer.flush()
                    del received_buffer[base]
                    base += 1

        elif header.type == END:
            end_seq = header.seq_num
            ack_packet = make_packet(ACK, end_seq + 1)
            sock.sendto(ack_packet, sender_address)
            break

    sock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("listen_ip")
    parser.add_argument("listen_port", type=int)
    parser.add_argument("window_size", type=int)
    args = parser.parse_args()

    receiver(args.listen_ip, args.listen_port, args.window_size)


if __name__ == "__main__":
    main()
