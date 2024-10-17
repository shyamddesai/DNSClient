# DNS Client
A Python-based DNS client that performs DNS lookups and interprets responses, supporting multiple query types (`A`, `MX`, and `NS`). The client includes error handling, retry logic, and packet parsing capabilities, making it suitable for basic DNS query testing.


## Basic Usage
### Command Syntax
python dnsClient.py [options] @server domain
- `@server`: The IP address of the DNS server to query (prefixed with `@`, e.g., `@8.8.8.8`).
- `domain`: The domain name to resolve (e.g., `mcgill.ca`).

### Options
- `-t <timeout>`: Set the timeout interval in seconds (default: 5).
- `-r <retries>`: Specify the number of retries on timeout (default: 3).
- `-p <port>`: Set the DNS server port (default: 53).
- `-mx`: Query for Mail Exchange (MX) records.
- `-ns`: Query for Name Server (NS) records.


## Examples
### Basic Queries
- Query for an A record:
`python dnsClient.py -t 5 -r 2 @8.8.8.8 mcgill.ca`

- Query for MX records:
`python dnsClient.py -mx @8.8.8.8 mcgill.ca`

- Query for NS records on a custom port:
`python dnsClient.py -ns -p 53 @1.1.1.1 example.com`

#### Expected Output
For a valid query, the output may look like:
```
Response received after 0.022 seconds (0 retries)
====== DNS Query Responses (2 records) ======
NS      pens2.mcgill.ca 3600    IN      NS
NS      pens1.mcgill.ca 3600    IN      NS
```

### Improper Queries
These commands showcase error handling for invalid inputs and configurations:
 - No Arguments:
`python dnsClient.py`

 - Conflicting Query Types:
`python dnsClient.py -mx -ns @8.8.8.8 mcgill.ca`

- Missing @ in Server Address:
`python dnsClient.py -t 10 -r 2 -mx 8.8.8.8 mcgill.ca`

- Non-integer Retry Value:
`python dnsClient.py -r 2.5 -mx @8.8.8.8 mcgill.ca`

- Negative Timeout Value:
`python dnsClient.py -t -1 -mx @8.8.8.8 mcgill.ca`

---

## DNS Caching
DNS caching is crucial for optimizing query response times by storing the results of previous lookups. Although this client does not implement caching, it’s important to note that DNS caching can allow subsequent requests for the same domain to bypass the full recursive query process, leading to faster response times and reduced load on DNS servers. Typically, DNS records are cached for a duration specified by their TTL (time-to-live) value.

## Program Design
The DNS Client is encapsulated in the dnsClient.py script, with functions organized as follows:
- **\_\_init_\_**: Sets primary parameters, including server, domain, query type, timeout, and retries.
- **send_query**: Manages the entire query process, including retries and response parsing.
- **build_query**: Constructs the DNS query packet.
- **parse_response**: Parses and interprets the DNS response, including error codes and record details.
- **extract_name**: Handles compressed domain names in responses, ensuring accurate interpretation of DNS labels.

## Features
- **Query Types**: Supports A, MX, and NS record queries.
- **Error Handling**: Handles missing arguments, invalid values, and timeout/retry logic.
- **Compressed Name Parsing**: Decodes DNS responses with compressed domain names.

## Limitations
This client does not support all DNS record types or advanced error-handling scenarios seen in production DNS resolvers. For example, it may not handle non-standard DNS types or special RCODE failures beyond basic checks.

---

## Requirements
- **Python Version**: Python 3.x is required.
- **Internet Connection**: DNS queries will need access to the specified DNS server over the internet.


## Authors
Shyam Desai
