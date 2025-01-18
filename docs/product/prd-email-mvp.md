1. **Product Overview**  
   - **Product name and version**: CalendarThat Email v1
   - **Executive summary/purpose**: CalendarThat Email allows users to send any arbitrary text to an email address (new@calendarthat.com) and receive a reply with an .ics file, a gcal link, and an outlook link. The primary purpose of this service is to allow for the creation of calendar events from within an email client (a location where many people receive event-like invitations). The secondary purpose is to allow for creation of calendar events on both mobile and desktop devices (because both have email clients).

2. **Problem Statement**  
   - **Current pain points**: the current calendarthat website is outside of one of the primary scheduling domains -- the email client. CalendarThat Email lets us get there.

3. **Product Scope**  
   - **Features and capabilities**: 
      - Reads the full text of an email and sends it to the event_creator API, returning .ics gcal and outlook links
   - **Use cases and user stories**:  
      - I'm in my email client and I need to make a cal event
      - I'm on my phone and need to make a cal event

4. **Functional Requirements**  
   - Accept text
   - Reply to the original email with calendar details
   - **Error handling and edge cases**:  
      - TBD

5. **Non-Functional Requirements**  
   - **Security requirements**:  
      - Associate users with their email accounts (more or less automatic)

6. **User Interface**  

7. **Technical Specifications**  
   - **System architecture**:  
      - email_interface: a new django app to send, receive, and log email messages
         - Its main purpose is to convert incoming emails into arguments for the event_creator EventBuilder to accept
         - It also creates a simple reply message with the generated calendar infomation
   - **Third-party dependencies**:  
      - We'll use SendGrid's mail API to send and receive email

8. **Timeline and Milestones**  
   - Jan 18

9. **Success Criteria**  
   - It works

10. **Future Considerations**  
    - **Potential enhancements**:
      - Handle pdf or image input to the email
      - Allow the user to reply with modifications to the original caldendar event created
      - Prompt non-signed up users to sign up in the reply email (so that timezone info is better handled)
      - Style the email to look nicer (?)