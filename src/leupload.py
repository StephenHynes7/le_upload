import argparse
import ConfigParser
import logging
import socket
import ssl
import certifi
import time
# create logger
log = logging.getLogger('le_upload')
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)

config = ConfigParser.ConfigParser()


def bufcount(filename):
    f = open(filename)
    lines = 1
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines


def get_tokenised_log_entries(filename, token):
    total_lines = bufcount(filename)
    lines = 0
    log.info('Reading file..')
    log_entries = []
    for line in open(filename):
        lines += 1
        tokenized_line = token + ' ' + line
        log_entries.append(tokenized_line)
        log.info('Tokenized %s/%s lines' % (lines, total_lines))
    return log_entries


def write_file(filename, tokenized_filename, token):
    f = open(tokenized_filename, 'wb')
    content = get_tokenised_log_entries(filename, token)
    f.writelines(content)
    f.close()


def get_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = ssl.wrap_socket(
        sock=sock,
        keyfile=None,
        certfile=None,
        server_side=False,
        cert_reqs=ssl.CERT_REQUIRED,
        ssl_version=getattr(
            ssl,
            'PROTOCOL_TLSv1_2',
            ssl.PROTOCOL_TLSv1
        ),
        ca_certs=certifi.where(),
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
    )
    try:

        sock.connect(("data.logentries.com", 443))
    except socket.error:
        log.fatal("Unable to connect to Logentries.")
        exit()
    conn = sock
    return conn


def upload(conn, line):
    conn.send(line)


def upload_to_logentries(filename):
    log.info('Beginning to send to Logentries')
    total_lines = bufcount(filename)
    start = time.time()
    conn = get_connection()
    lines = 0
    for line in open(filename):
        try:
            upload(conn, line)
            lines += 1
            log.info('Sent %s/%s lines' % (lines, total_lines))
        except socket.error:
            try:
                log.error('Lost connection to Logentries. Attempting to reconnect')
                upload(get_connection(), line)
            except socket.error:
                log.fatal("Error. Could not send log line number %s %s to Logentries" % (lines, line))
    end = time.time()
    log.info('Finished sending %s lines to Logentries, time elapsed %s seconds' % (lines, end-start))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('action', choices=['write', 'upload'], help='Use write to write local tokenized log file. Use upload'
                                                                'to send a file to Logentries.')
    ap.add_argument('filename', help='The file to be tokenized/uploaded.')
    ap.add_argument('--tokenized_filename', help='The filename to be created for a tokenized file.')
    ap.add_argument('--token', help='The token to be prepended to all log messages.')
    args = ap.parse_args()
    if args.action == 'write':
        write_file(args.filename, args.tokenized_filename, args.token)
    elif args.action == 'upload':
        upload_to_logentries(args.filename)

