# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


def test_cisco_acs_single(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ACS
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Single_Authentications: 0765855540 1 0 {{ date }} {{ time }} {{ tzoffset }} 0178632943 5202 NOTICE Device-Administration: Field1, Field2\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cisco:acs"'
    )
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_cisco_acs_multi(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ACS
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Multi_Authentications: 0000000002 2 0 {{ date }} {{ time }} {{ tzoffset }} 0000008450 5203 NOTICE Device-Administration: Field1, Field2, \n{{ mark }} {{ bsd }} {{ host }} CSCOacs_Multi_Authentications: 0000000002 2 1 Field3, Field4,\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    # First did we merge the events
    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cisco:acs" "Field1" Field4'
    )
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

    # First did we dupe the events
    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cisco:acs" "Field1"'
    )
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_cisco_acs_multi_lost(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Cisco ACS
    time = time[:-3]
    tzoffset = tzoffset[0:3] + ":" + tzoffset[3:]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CSCOacs_Multi_Authentications: 0000000002 3 0 {{ date }} {{ time }} {{ tzoffset }} 0000008450 5203 NOTICE Device-Administration: Field1, Field2, \n{{ mark }} {{ bsd }} {{ host }} CSCOacs_Multi_Authentications: 0000000002 3 1 Field3, Field4,\n"
    )
    message = mt.render(
        mark="<165>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    # First did we merge the events
    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cisco:acs" "Field1" Field4'
    )
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

    # First did we dupe the events
    st = env.from_string(
        'search _time={{ epoch }} index=netauth host="{{ host }}" sourcetype="cisco:acs" "Field1"'
    )
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
