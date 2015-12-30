#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: choices
Created: 12/29/15 3:33 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'


ACTIVITY_NOTIFY_CHOICES = (('N', "No Notifications"),
                           ('E', "Email Message"),
                           ('T', "Text Message")
                           )

BOOLEAN_CHOICES = (('1', 'Update'), ('0', 'Keep unchanged'))

# Carrier Selection shows carriers with their email address
# All names must be unique
CARRIER_SELECTION = (('NONE', 'None'),
                     ('3 river wireless', '3 river wireless(@sms.3rivers.net)'),
                     ('acs wireless', 'acs wireless(@paging.acswireless.com)'),
                     ('alltel', 'alltel(@message.alltel.com)'),
                     ('at&t', 'at&t(@txt.att.net)'),
                     ('bell canada', 'bell canada(@bellmobility.ca)'),
                     ('bell mobility txt', 'bell mobility(@txt.bellmobility.ca)'),
                     ('bell mobility (canada)', 'bell mobility (canada)(@txt.bell.ca)'),
                     ('blue sky frog', 'blue sky frog(@blueskyfrog.com)'),
                     ('bluegrass cellular', 'bluegrass cellular(@sms.bluecell.com)'),
                     ('boost mobile', 'boost mobile(@myboostmobile.com)'),
                     ('bpl mobile', 'bpl mobile(@bplmobile.com)'),
                     ('carolina west wireless', 'carolina west wireless(@cwwsms.com)'),
                     ('cellular one', 'cellular one(@mobile.celloneusa.com)'),
                     ('cellular south', 'cellular south(@csouth1.com)'),
                     ('centennial wireless', 'centennial wireless(@cwemail.com)'),
                     ('centurytel', 'centurytel(@messaging.centurytel.net)'),
                     ('cingular (now at&t)', 'cingular (now at&t)(@txt.att.net)'),
                     ('clearnet', 'clearnet(@msg.clearnet.com)'),
                     ('comcast', 'comcast(@comcastpcs.textmsg.com)'),
                     ('corr wireless communications', 'corr wireless communications(@corrwireless.net)'),
                     ('dobson', 'dobson(@mobile.dobson.net)'),
                     ('edge wireless', 'edge wireless(@sms.edgewireless.com)'),
                     ('fido', 'fido(@fido.ca)'),
                     ('golden telecom', 'golden telecom(@sms.goldentele.com)'),
                     ('helio', 'helio(@messaging.sprintpcs.com)'),
                     ('houston cellular', 'houston cellular(@text.houstoncellular.net)'),
                     ('idea cellular', 'idea cellular(@ideacellular.net)'),
                     ('illinois valley cellular', 'illinois valley cellular(@ivctext.com)'),
                     ('inland cellular telephone', 'inland cellular telephone(@inlandlink.com)'),
                     ('mci', 'mci(@pagemci.com)'),
                     ('metro pcs', 'metro pcs(@mymetropcs.com)'),
                     ('metrocall', 'metrocall(@page.metrocall.com)'),
                     ('metrocall 2-way', 'metrocall 2-way(@my2way.com)'),
                     ('microcell', 'microcell(@fido.ca)'),
                     ('midwest wireless', 'midwest wireless(@clearlydigital.com)'),
                     ('mobilcomm', 'mobilcomm(@mobilecomm.net)'),
                     ('mts', 'mts(@text.mtsmobility.com)'),
                     ('nextel', 'nextel(@messaging.nextel.com)'),
                     ('onlinebeep', 'onlinebeep(@onlinebeep.net)'),
                     ('pcs one', 'pcs one(@pcsone.net)'),
                     ('presidents choice', 'presidents choice(@txt.bell.ca)'),
                     ('public service cellular', 'public service cellular(@sms.pscel.com)'),
                     ('qwest', 'qwest(@qwestmp.com)'),
                     ('rogers at&t wireless', 'rogers at&t wireless(@pcs.rogers.com)'),
                     ('rogers canada', 'rogers canada(@pcs.rogers.com)'),
                     ('satellink', 'satellink(@satellink.net)'),
                     ('solo mobile', 'solo mobile(@txt.bell.ca)'),
                     ('southwestern bell', 'southwestern bell(@email.swbw.com)'),
                     ('sprint', 'sprint(@messaging.sprintpcs.com)'),
                     ('sumcom', 'sumcom(@tms.suncom.com)'),
                     ('surewest communications', 'surewest communications(@mobile.surewest.com)'),
                     ('t-mobile', 't-mobile(@tmomail.net)'),
                     ('telus', 'telus(@msg.telus.com)'),
                     ('tracfone', 'tracfone(@txt.att.net)'),
                     ('triton', 'triton(@tms.suncom.com)'),
                     ('unicel', 'unicel(@utext.com)'),
                     ('us cellular', 'us cellular(@email.uscc.net)'),
                     ('us west', 'us west(@uswestdatamail.com)'),
                     ('verizon', 'verizon(@vtext.com)'),
                     ('virgin mobile', 'virgin mobile(@vmobl.com)'),
                     ('virgin mobile canada', 'virgin mobile canada(@vmobile.ca)'),
                     ('west central wireless', 'west central wireless(@sms.wcc.net)'),
                     ('western wireless', 'western wireless(@cellularonewest.com)'),
                     )

# Use unique Carrier name to get email domain information
CARRIER_EMAIL_GATEWAY = (('None', 'NONE'),
                         ('3 river wireless', '@sms.3rivers.net'),
                         ('acs wireless', '@paging.acswireless.com'),
                         ('alltel', '@message.alltel.com'),
                         ('at&t', '@txt.att.net'),
                         ('bell canada', '@bellmobility.ca'),
                         ('bell canada', '@txt.bellmobility.ca'),
                         ('bell mobility txt', '@txt.bellmobility.ca'),
                         ('bell mobility (canada)', '@txt.bell.ca'),
                         ('blue sky frog', '@blueskyfrog.com'),
                         ('bluegrass cellular', '@sms.bluecell.com'),
                         ('boost mobile', '@myboostmobile.com'),
                         ('bpl mobile', '@bplmobile.com'),
                         ('carolina west wireless', '@cwwsms.com'),
                         ('cellular one', '@mobile.celloneusa.com'),
                         ('cellular south', '@csouth1.com'),
                         ('centennial wireless', '@cwemail.com'),
                         ('centurytel', '@messaging.centurytel.net'),
                         ('cingular (now at&t)', '@txt.att.net'),
                         ('clearnet', '@msg.clearnet.com'),
                         ('comcast', '@comcastpcs.textmsg.com'),
                         ('corr wireless communications', '@corrwireless.net'),
                         ('dobson', '@mobile.dobson.net'),
                         ('edge wireless', '@sms.edgewireless.com'),
                         ('fido', '@fido.ca'),
                         ('golden telecom', '@sms.goldentele.com'),
                         ('helio', '@messaging.sprintpcs.com'),
                         ('houston cellular', '@text.houstoncellular.net'),
                         ('idea cellular', '@ideacellular.net'),
                         ('illinois valley cellular', '@ivctext.com'),
                         ('inland cellular telephone', '@inlandlink.com'),
                         ('mci', '@pagemci.com'),
                         ('metro pcs', '@mymetropcs.com'),
                         ('metrocall', '@page.metrocall.com'),
                         ('metrocall 2-way', '@my2way.com'),
                         ('microcell', '@fido.ca'),
                         ('midwest wireless', '@clearlydigital.com'),
                         ('mobilcomm', '@mobilecomm.net'),
                         ('mts', '@text.mtsmobility.com'),
                         ('nextel', '@messaging.nextel.com'),
                         ('onlinebeep', '@onlinebeep.net'),
                         ('pcs one', '@pcsone.net'),
                         ('presidents choice', '@txt.bell.ca'),
                         ('public service cellular', '@sms.pscel.com'),
                         ('qwest', '@qwestmp.com'),
                         ('rogers at&t wireless', '@pcs.rogers.com'),
                         ('rogers canada', '@pcs.rogers.com'),
                         ('satellink', '@satellink.net'),
                         ('solo mobile', '@txt.bell.ca'),
                         ('southwestern bell', '@email.swbw.com'),
                         ('sprint', '@messaging.sprintpcs.com'),
                         ('sumcom', '@tms.suncom.com'),
                         ('surewest communications', '@mobile.surewest.com'),
                         ('t-mobile', '@tmomail.net'),
                         ('telus', '@msg.telus.com'),
                         ('tracfone', '@txt.att.net'),
                         ('triton', '@tms.suncom.com'),
                         ('unicel', '@utext.com'),
                         ('us cellular', '@email.uscc.net'),
                         ('us west', '@uswestdatamail.com'),
                         ('verizon', '@vtext.com'),
                         ('virgin mobile', '@vmobl.com'),
                         ('virgin mobile canada', '@vmobile.ca'),
                         ('west central wireless', '@sms.wcc.net'),
                         ('western wireless', '@cellularonewest.com'),
                         )

# 1 = Top level account access
# 2 = Backup level account access
# 9 or Standard Team member access
DEVELOPER_ROLE_CHOICES = (('1', 'Account Owner'),
                          ('2', 'Backup Owner'),
                          ('9', 'Team Member'),
                          ('-', 'None' ),
                         )

FORMAT_OPTIONS_CHOICES = ['json', 'xml']

USERTYPE_CHOICES = (('owner', 'Account Owner'))

USER_ROLE_CHOICES = (('primary', 'Account Owner'),
                     ('backup', 'Backup Owner'),
                     ('none', 'NONE'),
                     )

