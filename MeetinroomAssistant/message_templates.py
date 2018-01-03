#!/usr/bin/python3
# -*- coding: utf-8 -*-

#Sample message used to query calendar data. Remember to replace relevant parts of this message
sample_getcalendar_request = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages"
    xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <soap:Header>
      <t:RequestServerVersion Version="Exchange2010_SP2" />
   </soap:Header>
   <soap:Body>
      <m:FindItem Traversal="Shallow">
         <m:ItemShape>
            <t:BaseShape>IdOnly</t:BaseShape>
            <t:AdditionalProperties>
               <t:FieldURI FieldURI="item:Subject" />
               <t:FieldURI FieldURI="calendar:Start" />
               <t:FieldURI FieldURI="calendar:End" />
            </t:AdditionalProperties>
         </m:ItemShape>
         <m:CalendarView MaxEntriesReturned="10" StartDate="!Start_Date!" EndDate="!End_Date!" />
         <m:ParentFolderIds>
            <t:DistinguishedFolderId Id="calendar">
               <t:Mailbox>
                  <t:EmailAddress>!Replace_Email_Of_Calendar!</t:EmailAddress>
               </t:Mailbox>
            </t:DistinguishedFolderId>
         </m:ParentFolderIds>
      </m:FindItem>
   </soap:Body>
</soap:Envelope>'''

#Sample message used to make an appointment to the designated calendar. Remember to replace relevant parts of this message
sample_appointment_request = '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <soap:Body>
      <CreateItem xmlns="http://schemas.microsoft.com/exchange/services/2006/messages" SendMeetingInvitations="SendToAllAndSaveCopy">
         <SavedItemFolderId>
            <t:DistinguishedFolderId Id="calendar" />
         </SavedItemFolderId>
         <Items>
            <t:CalendarItem xmlns="http://schemas.microsoft.com/exchange/services/2006/types">
               <Subject>Ad-hoc varaus</Subject>
               <Body BodyType="Text"></Body>
               <ReminderIsSet>false</ReminderIsSet>
               <ReminderMinutesBeforeStart>60</ReminderMinutesBeforeStart>
               <Start>!Start_Date!</Start>
               <End>!End_Date!</End>
               <IsAllDayEvent>false</IsAllDayEvent>
               <LegacyFreeBusyStatus>Busy</LegacyFreeBusyStatus>
               <Location></Location>
               <RequiredAttendees>
                  <Attendee>
                     <Mailbox>
                        <EmailAddress>!Replace_Email_Of_Calendar!</EmailAddress>
                     </Mailbox>
                  </Attendee>
               </RequiredAttendees>
            </t:CalendarItem>
         </Items>
      </CreateItem>
   </soap:Body>
</soap:Envelope>'''


#Sample message used to delete an appointment from the designated calendar. Remember to replace relevant parts of this message
sample_delete_request = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types">
  <soap:Body>
    <DeleteItem DeleteType="HardDelete" SendMeetingCancellations="SendToAllAndSaveCopy" xmlns="http://schemas.microsoft.com/exchange/services/2006/messages">
      <ItemIds>
        <t:ItemId Id="!Replace_ItemId!"/>
      </ItemIds>
    </DeleteItem>
  </soap:Body>
</soap:Envelope>
'''
