# Chatter

Simple MVP chat application using Django+StimulusJS. This is an experiment using django async and channels as well as websockets.

## Spec

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

## Local setup

This requires docker and docker-compose be installed on your machine. More details here:

https://github.com/danjac/django-saas-starter

For local development:

    cp .env.example .env

Edit the environment variables as per the SAAS starter instructions.

    docker-compose up -d

Note: remember to change the default "Site" object domain to "localhost"!

## License

This project is covered by GNU Affero General Public License (AGPL).


