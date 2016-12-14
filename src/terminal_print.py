"""
The magic below which handles printing while waiting for input, is taken from stackoverflow
http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th
"""
import sys, readline, struct, termios, fcntl, time

def blank_current_readline():
    # Next line said to be reasonably portable for various Unixes
    (rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))

    text_len = len(readline.get_line_buffer())+2

    # ANSI escape sequences (All VT100 except ESC[0G)
    sys.stdout.write('\x1b[2K')                         # Clear current line
    sys.stdout.write('\x1b[1A\x1b[2K'*(text_len/cols))  # Move cursor up and clear line
    sys.stdout.write('\x1b[0G')                         # Move to start of line


def print_message(message):
        blank_current_readline()
        print(message)
        sys.stdout.write(readline.get_line_buffer())
        sys.stdout.flush()

def join_reporter(client):
    while True:
        client.channel.start_consuming()
        time.sleep(0.2)



