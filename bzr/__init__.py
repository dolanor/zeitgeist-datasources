# -.- coding: utf-8 -.-

# Zeitgeist
#
# Copyright © 2009 Markus Korn <thekorn@gmx.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Post-commit hook to submit the commit to Zeitgeist (http://www.zeitgeist-project.com)

Requires bzr 0.15 or higher.

Copyright (C) 2009, Markus Korn <thekorn@gmx.de>
Published under the GNU GPLv2 or later

Installation:
Copy this directory to ~/.bazaar/plugins/zeitgeist/*
"""

import time
import logging
from bzrlib import branch

logging.basicConfig(filename="/dev/null")

install_hook = True
CLIENT = None

try:
    from zeitgeist.client import ZeitgeistClient
    from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation
except ImportError:
    install_hook = False
else:
    try:
        CLIENT = ZeitgeistClient()
    except RuntimeError, e:
        print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
        install_hook = False


def post_commit(local, master, old_revno, old_revid, new_revno, new_revid):
    revision = master.repository.get_revision(new_revid)
    if new_revno == 1:
        interpretation = Interpretation.CREATE_EVENT
    else:
        interpretation = Interpretation.MODIFY_EVENT
    subject = Subject.new_for_values(
        uri=unicode(master.base),
        interpretation=unicode(Interpretation.SOURCE_CODE),
        manifestation=unicode(Manifestation.FILE_DATA_OBJECT),
        text=unicode(revision.message.rstrip()),
        origin=unicode(master.base),
    )
    event = Event.new_for_values(
        timestamp=int(time.time()*1000),
        interpretation=unicode(interpretation),
        manifestation=unicode(Manifestation.USER_ACTIVITY),
        actor="application://bzr.desktop", #something usefull here, always olive-gtk?
        subjects=[subject,]
    )
    CLIENT.insert_event(event)

if install_hook:
    branch.Branch.hooks.install_named_hook("post_commit", post_commit,
                                           "Zeitgeist dataprovider for bzr")
