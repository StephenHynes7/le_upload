# le_upload

usage: leupload.py [-h] [--tokenized_filename TOKENIZED_FILENAME]
                   [--token TOKEN]
                   {write,upload} filename

positional arguments:
  * {write,upload}        Use write to write local tokenized log file. Use
                        uploadto send a file to Logentries.
  * filename              The file to be tokenized/uploaded.

optional arguments:
  * -h, --help            show this help message and exit
  * --tokenized_filename TOKENIZED_FILENAME
                        The filename to be created for a tokenized file.
  * --token TOKEN         The token to be prepended to all log messages.