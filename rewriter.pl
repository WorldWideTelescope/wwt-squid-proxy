#! /usr/bin/perl
# Copyright 2020 the .NET Foundation
# Licensed under the MIT License

use URI::Escape;

$| = 1;

while (<>) {
    chomp;
    @items = split;
    my $channelid = $items[0];
    my $url = $items[1];
    my @protoitems = split /\/\//, $url, 2;

    if (scalar @protoitems != 2) {
        print "$channelid ERR\n";
        next;
    }

    my @pathitems = split /\//, $protoitems[1], 2;

    if (scalar @pathitems != 2) {
        print "$channelid ERR\n";
        next;
    }

    if ($pathitems[1] eq "") {
        print "$channelid OK status=302 url=\"http://healthy/\"\n";
        next;
    }

    my @delimited = split /\?targeturl=/, $pathitems[1], 2;

    if (scalar @delimited != 2) {
        print "$channelid ERR\n";
        next;
    }

    my ($pathprefix, $targeturl) = @delimited;
    $targeturl = uri_unescape($targeturl);

    # FIXME: we're taking it on faith that the target URL contains no " marks.

    if (lc($pathprefix) eq 'webserviceproxy.aspx') {
        print "$channelid OK rewrite-url=\"$targeturl\"\n";
    } elsif (lc($pathprefix) eq 'wwtweb/webserviceproxy.aspx') {
        print "$channelid OK rewrite-url=\"$targeturl\"\n";
    } else {
        print "$channelid ERR\n";
    }
}
