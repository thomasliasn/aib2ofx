#!/usr/bin/env python
# coding: utf-8

import optparse, re

import aib, cfg, ofx


def getOptions():
    parser = optparse.OptionParser()
    option_list = [
        optparse.make_option(
            '-d', '--output-dir',
            dest='output_dir', help='directory to put OFX files in [/tmp]'
        ),
    ]
    parser.add_options(option_list)
    parser.set_defaults(output_dir='/tmp')
    return parser.parse_args()


def getData(user, config, output_dir, formatter):
    cleanup_re = re.compile('[- 	]+')

    # Login to the bank, scrape data for all accounts.
    creds = config[user]
    bank = aib.aib(creds)
    bank.login()
    bank.scrape()
    bank.bye()

    # Save each account to separate OFX file.
    for account in bank.getdata().values():
        name = re.sub(cleanup_re,
                      '_',
                      account['accountId']).lower()
        f = open(
            '%s/%s_%s.ofx' % (output_dir, user, name),
            'w'
        )
        f.write(formatter.prettyprint(account))
        f.close


def main():
    # Parse command line options.
    (options, args) = getOptions()

    # Read user-provided credentials.
    config = cfg.config()
    formatter = ofx.ofx()

    # Iterate through accounts, scrape, format and save data.
    for user in config.users():
        getData(user, config, options.output_dir, formatter)


if __name__ == '__main__':
    main()
