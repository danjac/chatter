# Chatter

Simple MVP chat application using Django+StimulusJS. This is an experiment using django async and channels as well as websockets.

Requirements v0.1

This is a very simple implementation for a hypothetical small company.

- users can create a new chat room
- messages are rendered in Markdown
- all chat rooms are shown in the left nav column
- left nav column in mobile is togglable with a "bars" button in top nav
- you can invite another user by typing "@" plus their username
- typing "@" in a chat shows typeahead with fullname/username
- if a chat room in left nav has new message it should be highlighted
- if someone in a chat room "@" messages me it should have some other indicator as well
- if a user "owns" a room they can archive it. Archived rooms should be shown in a separate page.
- the navbar has a search field to find messages. Message results are banded into chat rooms.

These features would likely be needed in any "serious" production app but are not included for this POC:

- an email invite system which would only allow invited users to join the site
- private/invite-only chat rooms
- ability to edit and delete your own messages
- browser or in-app notifications when a new message is received
