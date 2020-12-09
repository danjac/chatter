# Chatter

Simple MVP chat application using Django+StimulusJS. This is an experiment using django async and channels as well as websockets.

Requirements v0.1

This is a very simple implementation for a hypothetical small company. We'll assume there are no "private" rooms; you can see and join a chat at any time. The chat messages are text only i.e. no uploaded images, emojis etc although simple Markdown is allowed.

- users can create a new chat room
- all chat rooms are shown in the left nav column
- left nav column in mobile is togglable with a "bars" button in top nav
- you can invite another user by typing "@" plus their username
- typing "@" in a chat shows typeahead with fullname/username
- if a chat room in left nav has new message it should be highlighted
- if someone in a chat room "@" messages me it should have some other indicator as well
- if a user "owns" a room they can archive it. Archived chats are dimmed, appear at the bottom, and are read-only.
- the navbar has a search field to find messages. Message results are banded into chat rooms.
- you can opt into browser notifications. When a user sends you a message the notification "X has sent you a message" should appear, linked to the chatroom, *unless* you happen to be in the chatroom at the time.
