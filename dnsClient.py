import socket
import sys
import struct
import random
import time
import argparse

class DnsClient:
    def __init__(self, server, query_name, query_type="A", timeout=5, max_retries=3, port=53):
        # Initialize the DNS client with server IP, query name, query type, timeout, retries, and port
        self.server = server
        self.query_name = query_name
        self.query_type = query_type
        self.timeout = timeout
        self.max_retries = max_retries
        self.port = port
        self.query_types = {"A": 1, "MX": 15, "NS": 2, "CNAME": 5}  # Query type requirements

    def send_query(self):
        # Build the DNS query packet
        query = self.build_query()
        attempt = 0  # Number of retry attempts

        while attempt < self.max_retries:
            try:
                # Create a UDP socket
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(self.timeout)  # Set socket timeout
                    start_time = time.time()  # Record start time for response time calculation

                    # Send the query to the DNS server
                    sock.sendto(query, (self.server, self.port))

                    # Receive the response from the server
                    response, _ = sock.recvfrom(512)
                    response_time = time.time() - start_time  # Calculate response time

                    # Parse and print the DNS response
                    self.parse_response(response, response_time, attempt)
                    return
            except socket.timeout:
                attempt += 1  # Increment retry count on timeout
                print(f"Retry {attempt}/{self.max_retries} due to timeout...")

        # If max retries reached without a response, print an error message
        print("ERROR: Maximum retries reached without response.")

    def build_query(self):
        # Construct the DNS query packet with the help of dnsprimer
        transaction_id = random.randint(0, 65535)  # Unique ID for the DNS query
        flags = 0x0100  # Standard query with recursion
        qdcount = 1  # Number of questions in the query

        # DNS header structure
        header = struct.pack(">HHHHHH", transaction_id, flags, qdcount, 0, 0, 0)

        # Encode the domain name in the question section
        question = b"".join(struct.pack("B", len(part)) + part.encode() for part in self.query_name.split("."))
        question += b"\x00"  # End of domain name

        # Define query type (A, MX, NS, etc.) and class (IN for internet)
        qtype = struct.pack(">H", self.query_types.get(self.query_type, 1))  # Default to A if not specified
        qclass = struct.pack(">H", 1)  # Class IN (Internet)

        # Combine header and question sections to form the complete DNS query
        return header + question + qtype + qclass

    def parse_response(self, response, response_time, retries):
        # Parse the DNS response packet
        header = struct.unpack(">HHHHHH", response[:12])
        transaction_id, flags, qdcount, ancount, nscount, arcount = header

        if ancount == 0:
            # If no answers are found, print NOTFOUND
            print("NOTFOUND")
            return

        # Print response summary
        print(f"Response received after {response_time:.3f} seconds ({retries} retries)")
        print(f"====== DNS Query Responses ({ancount} records) ======")

        # Skip the question section in the response packet
        offset = 12
        for _ in range(qdcount):
            offset = self.skip_name(response, offset) + 4

        # Print each answer record in the Answer section
        for _ in range(ancount):
            offset = self.print_record(response, offset)

    def skip_name(self, message, offset):
        # Skip the encoded domain name in the response
        while message[offset] != 0:
            if message[offset] >= 192:  # Pointer to another part of the message
                return offset + 2
            offset += message[offset] + 1  # Move to the next label
        return offset + 1  # Skip the null byte at the end of the name

    def print_record(self, response, offset):
        # Print a single DNS record from the response
        offset = self.skip_name(response, offset)  # Skip the record name
        rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", response[offset:offset + 10])
        offset += 10  # Move past the fixed part of the record

        # Identify the record type (A, MX, NS, or CNAME)
        record_type = {1: "A", 2: "NS", 5: "CNAME", 15: "MX"}.get(rtype, "Unknown")
        if rtype == 1:  # A record (IPv4 address)
            ip = ".".join(map(str, response[offset:offset + rdlength]))
            print(f"IP\t{ip}\t{ttl}\tIN\tA")
        elif rtype == 2 or rtype == 5:  # NS or CNAME record
            cname = self.extract_name(response, offset)
            print(f"{record_type}\t{cname}\t{ttl}\tIN\t{record_type}")
        elif rtype == 15:  # MX record
            preference = struct.unpack(">H", response[offset:offset + 2])[0]
            exchange = self.extract_name(response, offset + 2)
            print(f"MX\t{exchange}\t{preference}\t{ttl}\tIN\tMX")
        
        return offset + rdlength  # Return the updated offset after the record data

    def extract_name(self, message, offset):
        # Extract a domain name from the message using DNS label compression
        labels = []
        while message[offset] != 0:
            if message[offset] >= 192:  # Compression pointer
                pointer = struct.unpack(">H", message[offset:offset + 2])[0] & 0x3FFF
                labels.append(self.extract_name(message, pointer))  # Follow pointer recursively
                offset += 2
                break
            else:
                length = message[offset]
                labels.append(message[offset + 1:offset + 1 + length].decode())
                offset += length + 1  # Move to the next label
        return ".".join(labels)  # Join all labels to form the full domain name

if __name__ == "__main__":
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="DNS Client")
    parser.add_argument("-t", type=int, default=5, help="Timeout in seconds (default 5)")
    parser.add_argument("-r", type=int, default=3, help="Maximum number of retries (default 3)")
    parser.add_argument("-p", type=int, default=53, help="DNS server port (default 53)")
    parser.add_argument("-mx", action="store_true", help="Query for MX records")
    parser.add_argument("-ns", action="store_true", help="Query for NS records")
    parser.add_argument("server", type=str, help="DNS server IP address")
    parser.add_argument("name", type=str, help="Domain name to query")
    
    args = parser.parse_args()

    # Validate that only one of -mx or -ns is specified
    if args.mx and args.ns:
        print("ERROR: Only one of -mx or -ns can be specified at a time.")
        sys.exit(1)

    # Validate that timeout is positive
    if args.t <= 0:
        print("ERROR: Timeout (-t) must be a positive integer.")
        sys.exit(1)

    # Validate that max retries is non-negative
    if args.r < 0:
        print("ERROR: Maximum retries (-r) must be a non-negative integer.")
        sys.exit(1)

    # Check that the server argument starts with "@"
    if not args.server.startswith("@"):
        print("ERROR: Server address must be prefixed with '@'. For example: @8.8.8.8")
        sys.exit(1)

    # Strip "@" from server address
    server = args.server[1:]

    # Determine the query type based on flags
    query_type = "A"
    if args.mx:
        query_type = "MX"
    elif args.ns:
        query_type = "NS"
    
    # Create and run the DNS client
    client = DnsClient(server=server, query_name=args.name, query_type=query_type, timeout=args.t, max_retries=args.r, port=args.p)
    client.send_query()