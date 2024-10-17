# DNS Client

A Python-based DNS client that performs DNS lookups and interprets responses, supporting multiple query types (`A`, `MX`, and `NS`). The client is designed to handle various DNS query scenarios with error management, retry logic, and packet parsing.

## Requirements

- Python 3.x
- Internet connection for DNS queries

### Basic Syntax
python dnsClient.py [options] @server domain
    @server: IP address of the DNS server (prefixed with @, e.g., @8.8.8.8)
    domain: Domain name to query (e.g., mcgill.ca)

### Options
    -t <timeout>: Set timeout in seconds (default: 5).
    -r <retries>: Number of retries on timeout (default: 3).
    -p <port>: DNS server port (default: 53).
    -mx: Query for Mail Exchange (MX) records.
    -ns: Query for Name Server (NS) records.

## Examples
# Query for an A record
python dnsClient.py -t 5 -r 2 @8.8.8.8 mcgill.ca

# Query for MX records
python dnsClient.py -mx @8.8.8.8 mcgill.ca

# Query for NS records with custom port
python dnsClient.py -ns -p 53 @1.1.1.1 example.com