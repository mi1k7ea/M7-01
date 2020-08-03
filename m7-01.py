# coding=utf-8

from lib.input_parser import input_parse
from bruter import WebDirBruter
from lib.banner import show_banner

def main():
    show_banner()
    params = input_parse()
    scanner = WebDirBruter(params)
    scanner.start()

if __name__ == '__main__':
    main()