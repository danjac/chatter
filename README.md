# Chatter

Simple MVP chat application using Django+StimulusJS. This is an experiment using django async and channels as well as websockets.

Requirements v0.1

This is a very simple implementation for a hypothetical small company.

- users can create a new chat room
- messages are rendered in Markdown
- all chat rooms are shown in the left nav column
- left nav column in mobile is togglable with a "bars" button in top nav
- you can invite another user by typing "@" plus their username
- if a chat room in left nav has new message it should be highlighted
- if someone in a chat room "@" messages me it should have some other indicator as well
- the navbar has a search field to find messages. Message results are banded into chat rooms.

These features would likely be needed in any "serious" production app but are not included for this POC:

- an email invite system which would only allow invited users to join the site
- private/invite-only chat rooms
- ability to edit and delete your own messages
- browser or in-app notifications when a new message is received
- typeahead to find other user when typing "@" and a name
- archive/delete rooms if owner

A production deployment should also use Daphne or Uvicorn as channel backend.

## Architecture

Specific parts of the site we want to update asynchronously are demarcated with a Stimulus socket controller. This controller automatically reloads the content of the element with an AJAX request if the specific group/type match the websocket data.

Another approach - similar to the LiveView or Stimulus-Reflex pattern, would be to render and push the content itself in the channel consumer. The content could be separated into different "sections" and the client socket controllers could specify which section they would refresh when a new message is pushed. For example, one section could be "sidebar", and the socket controller for the sidebar would refresh the element with this content.
